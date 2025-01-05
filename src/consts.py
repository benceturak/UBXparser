gnssID = {
    0: ('G', 'GPS', 'GPS'),
    1: ('S', 'SBAS', 'SBAS'),
    2: ('E', 'GAL', 'Galileo'),
    3: ('B', 'BDS', 'BeiDou'),
    #4: ('I', 'IMES', 'IMES'),
    5: ('Q', 'QZSS', 'QZSS'),
    6: ('R', 'GLO', 'GLONASS'),
    7: ('N', 'NavIC', 'NavIC')
}

satID = {

}

sigID = {
    0: {
        0: ('L1C', 'L1 C/A'),
        3: ('L2CL', 'L2 CL'),
        4: ('L2CM', 'L2 CM'),
        6: ('L5I', 'L5 I'),
        7: ('L5Q', 'L5 Q')
    },
    1: {
        0: ('L1', 'L1 C/A2')
    },
    2: {
        0: ('L1C', 'E1 C'),
        1: ('E1B', 'E1 B'),
        3: ('E5aI', 'E5a I'),
        4: ('E5aQ', 'E5a Q'),
        5: ('E5bI', 'E5b I'),
        6: ('E5bQ', 'E5b Q')
    },
    3: {
        0: ('B1D1', 'B1|D1'),
        1: ('B1D2', 'B1|D2'),
        2: ('B2D1', 'B2|D1'),
        3: ('B2D2', 'B2|D2'),
        5: ('B1C', 'B1C'),
        7: ('B2a', 'B2a'),
    },
    5: {
        0: ('L1CA', 'L1 C/A'),
        1: ('L1S', 'L1 S'),
        2: ('L2CM', 'L2 CM'),
        3: ('L2CL', 'L2 CL'),
        5: ('L5I', 'L5 I'),
        7: ('L5Q', 'L5 Q'),
    },
    6: {
        0: ('L1C', 'L1 OF'),#!!!!!!!!
        2: ('L2', 'L2 OF')
    },
    7: {
        0: ('L5A', 'L5A')
    }
    
}

sigIdRINEX = {
    0: {
        "1C": 0,
        "2S": 3,
        "2M": 4,
        "5I": 6,
        "5Q": 7
    },
    1: {
        "1C": 0
    },

    2: {
        "1C": 0,
        "1B": 1,
        "5I": 3,
        "5Q": 4,
        "7I": 5,
        "7Q": 6
    }
    
}