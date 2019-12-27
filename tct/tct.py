import struct
from datetime import datetime
import numpy as np


def read(filename):
    """
    Read a data file from PSTCT by Particulars. It returns two objects: metadata and data. Example:

        medatada, data = read('filename.rtct')
    """
    def read_fmt(f, fmt):
        struct_len = struct.calcsize(fmt)
        return struct.unpack(fmt, f.read(struct_len))

    f = open(filename, 'rb')

    struct_fmt = "f6ff9f"
    struct_len = struct.calcsize(struct_fmt)
    struct_unpack = struct.Struct(struct_fmt).unpack_from

    metadata = dict(zip(('filetype', 'day', 'month', 'year', 'hour', 'minutes', 'seconds',
                          'abstime', 'x0', 'dx', 'nx', 'y0', 'dy', 'ny', 'z0', 'dz', 'nz'), struct_unpack(f.read(struct_len))))

    for field in 'nx', 'ny', 'nz', 'filetype', 'day', 'month', 'year', 'hour', 'minutes', 'seconds':
        metadata[field] = int(metadata[field])
        
    metadata['time'] = datetime(metadata['year'], metadata['month'], metadata['day'], metadata['hour'], metadata['minutes'], metadata['seconds'])

    if metadata['filetype'] in (33, 51, 81, 82):
       ofs=1
    else:
       ofs=0

    wfonoff_fmt = "4f" if ofs == 1 else "3f"
    wfonoff_len = struct.calcsize(wfonoff_fmt)
    metadata['wfonoff'] = list(map(int, struct.unpack(wfonoff_fmt, f.read(wfonoff_len))))

    metadata['nu1'] = int(read_fmt(f, 'f')[0])
    metadata['u1'] = np.fromfile(f, dtype=np.float32, count=metadata['nu1'])
    metadata['nu2'] = int(read_fmt(f, 'f')[0])
    metadata['u2'] = np.fromfile(f, dtype=np.float32, count=metadata['nu2'])
    metadata['t0'], metadata['dt'], metadata['NP'] = read_fmt(f, 'fff')
    if abs(metadata['t0']) > 1E-3: metadata['t0'] *= 1E-9
    if abs(metadata['dt']) > 1E-3: metadata['dt'] *= 1E-9
    metadata['NP'] = int(metadata['NP'])

    if metadata['filetype'] in (82, 81, 51, 33):
        metadata['T'] = read_fmt(f, 'f')[0]
        metadata['source'] = int(read_fmt(f, 'f')[0])

        size_user = read_fmt(f, 'i')[0]
        metadata['user'] = (b''.join(read_fmt(f, '%dc' % (size_user)))).decode('ascii')

        size_sample = read_fmt(f, 'i')[0]
        metadata['sample'] = (b''.join(read_fmt(f, '%dc' % (size_sample)))).decode('ascii')

        size_comment = read_fmt(f, 'i')[0]
        metadata['comment'] = (b''.join(read_fmt(f, '%dc' % (size_comment)))).decode('ascii')
    elif metadata['filetype'] == 22:
        pass

    """
      // int ix; index valuex = event;
      //xyz values :
      //0 - x
      //1 - y
      //2 - z
      //3 - U1
      //4 - U2
      //5 - I1
      //6 - I2
      //7 - Beam monitor
      //8 - time
      //9 - T laser 
      //10 - T box
      //11 - Vtresh
      12 .. 21 are user data
    """

    data_fields = 'x', 'y', 'z', 'u1', 'u2', 'i1', 'i2', 'beam monitor', 'time', 'T laser', 'T box', 'Vtresh', 'ch1', 'ch2', 'ch3', 'ch4'
    data = {field: [] for field in data_fields}

    for iu1 in range(metadata['nu1']):
        for iu2 in range(metadata['nu2']):
            tU1, tU2, tI1, tI2 = np.fromfile(f, dtype=np.float32, count=4)
            for ixyz in range(metadata['nx'] * metadata['ny'] * metadata['nz']):
                x, y, z = np.fromfile(f, dtype=np.float32, count=3)
                beam_monitor = read_fmt(f, 'f')[0]
                data['x'].append(x)
                data['y'].append(y)
                data['z'].append(z)
                data['u1'].append(tU1)
                data['u2'].append(tU2)
                data['i1'].append(tI1)
                data['i2'].append(tI2)

                data['beam monitor'].append(beam_monitor)
                if metadata['filetype'] == 51:
                    data['time'].append(read_fmt(f, 'f')[0])
                elif metadata['filetype'] == 81:
                    data['time'].append(read_fmt(f, 'f')[0])
                    data['T laser'].append(read_fmt(f, 'f')[0])
                    data['T box'].append(read_fmt(f, 'f')[0])
                elif metadata['filetype'] == 82:
                    buf = read_fmt(f, '10f')
                    for field, value in zip(data_fields[8:12], buf):
                        data[field].append(value)
                    user_data = np.fromfile(f, dtype=np.float32, count=4)
                for channel in range(4):
                    if metadata['wfonoff'][channel]:
                        data['ch%d' % (channel + 1)].append(np.fromfile(f, dtype=np.float32, count=metadata['NP']))

    for k, v in data.items():
        data[k] = np.array(v)
        
    return metadata, data