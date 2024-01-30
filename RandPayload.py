import struct
import random


class RandPayload:
    def __init__(self):
        self.DATA_TYPE = [0x1, 0x2, 0x3, 0x4]
        self.TARGET_BUF_ID = [0x3, 0x0A, 0x0B, 0x0C, 0x0D, 0x7D, 0x7E, 0x7F]
        self.MAX_CLS_SIZE = 0xff
        self.MAX_CMD_SIZE = 0x10  # MAX actual data size (total size - size of header)
        self.HEADER_SIZE = 0x7  # size of header
        self.RANDOM_SIZE = [i for i in range(8, 40)]

        self.PRJ_ID = [0X0, 0X1, 0X2, 0X3, 0X4, 0X8]     # 1 byte
        self.FEAT_ID = [i for i in range(133, 177)]      # 1 byte
        self.CLS_NUM = {0X0: 31, 0X1: 35, 0X2: 19, 0X3: 23, 0X4: 26, 0X8: 17}


    def generate_random_data(self):
        # project ID
        if random.randint(0,1) == 0:
            prj_feat_id = random.choice(self.PRJ_ID)
            cls_num = self.CLS_NUM[prj_feat_id]
        # feature ID
        else: 
            prj_feat_id = random.choice(self.FEAT_ID)
            cls_num = random.randint(1, self.MAX_CLS_SIZE)
        
        cls_id = random.randint(1, cls_num)
        cmd_id = random.randint(1, self.MAX_CLS_SIZE)
        cmd_data_size = random.randint(1, self.MAX_CMD_SIZE)
        cmd_data = bytes([random.randint(0, 255) for _ in range(cmd_data_size)])

        data = struct.pack(
            "<BBH", prj_feat_id, cls_id, cmd_id
        )
        data += cmd_data
        
        return data

    def generate_random_payload(self, seq):
        data_type = random.choice(self.DATA_TYPE)
        target_buffer_id = random.choice(self.TARGET_BUF_ID)
        actual_data = self.generate_random_data()
        
        # Construct the data frame
        data_frame = struct.pack(
            "<BBBI", data_type, target_buffer_id, seq, len(actual_data) + self.HEADER_SIZE
        )
        data_frame += actual_data

        return data_frame

    def generate_real_random(self, seq):
        data_type = random.choice(self.DATA_TYPE)
        target_buffer_id = random.choice(self.TARGET_BUF_ID)
        data_size = random.choice(self.RANDOM_SIZE)
        actual_data = bytes([random.randint(0, 255) for _ in range(data_size)])
        
        # Construct the data frame
        data_frame = struct.pack(
            "<BBBI", data_type, target_buffer_id, seq, len(actual_data) + self.HEADER_SIZE
        )
        data_frame += actual_data

        return data_frame


# for seq in range(10):
#     random_data = generate_random_header(seq)
#     print(random_data.hex(), end="\n\n")
