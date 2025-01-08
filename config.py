event_ids = dict(
    s1=3, s2=5, s3=9,
    s4_0=19, s5_0=21, s6_0=25,
    s4_15=35, s5_15=37, s6_15=41,
    w0_hit=337, w15_hit=353,
    o0_cr=400, o15_cr=416,
    w0_miss=593, w15_miss=609,
    o0_fa=656, o15_fa=672
    )

recordings = [
    dict(subject='0001', date='20210810_000000', mr_date='20191015_121553', bad_channels = ['MEG0232', 'MEG0321', 'MEG0422', 'MEG2613']),
    dict(subject='0002', date='20210804_000000', mr_date='20191015_112257', bad_channels = ['MEG0121', 'MEG0422', 'MEG0441', 'MEG1133', 'MEG2613']),
    dict(subject='0003', date='20210802_000000', mr_date='20210812_102146', bad_channels = ['MEG0321', 'MEG0422', 'MEG1133', 'MEG2523']),
    # dict(subject='0004', date='20210728_000000', mr_date='20210811_164949'), NO RESPIRATION DATA
    # dict(subject='0005', date='20210728_000000', mr_date='20210816_091907'), CHECK THIS ONE AGAIN - maybe resp channel name is different...
    # dict(subject='0006', date='20210728_000000', mr_date='20210811_173642'), NO RESPIRATION DATA
    # dict(subject='0007', date='20210728_000000', mr_date='20210812_105728'), NO RESPIRATION DATA
    # dict(subject='0008', date='20210730_000000', mr_date='20210812_081520'), NO RESPIRATION DATA
    # dict(subject='0009', date='20210730_000000', mr_date='20210812_141341'), NO RESPIRATION DATA
    # dict(subject='0010', date='20210730_000000', mr_date='20210812_094201'), NO RESPIRATION DATA
    # dict(subject='0011', date='20210730_000000', mr_date='20191015_104445'), NO RESPIRATION DATA
    dict(subject='0012', date='20210802_000000', mr_date='20210812_145235', bad_channels = ['MEG0221','MEG0422', 'MEG2613']),
    dict(subject='0013', date='20210802_000000', mr_date='20210811_084903', bad_channels = ['MEG0422', 'MEG0932', 'MEG2613']),
    dict(subject='0014', date='20210802_000000', mr_date='20210812_164859', bad_channels = ['MEG0321', 'MEG0422', 'MEG0811', 'MEG2613']),
    # dict(subject='0015', date='20210804_000000', mr_date='20210811_133830', bad_channels = ['MEG0422', 'MEG1133', 'MEG2613']),  # NO RESPIRATION DATA? Looks very noisy atleast
    dict(subject='0016', date='20210804_000000', mr_date='20210812_153043', bad_channels = ['MEG0422', 'MEG1133', 'MEG2613']),
    # dict(subject='0017', date='20210805_000000', mr_date='20210820_123549', bad_channels = ['MEG0422', 'MEG0613', 'MEG1133', 'MEG2613']), NO RESPIRATION DATA
    dict(subject='0018', date='20210805_000000', mr_date='20210811_113632', bad_channels = ['ECG003', 'MEG0422', 'MEG0613', 'MEG1133', 'MEG2613']),
    dict(subject='0019', date='20210805_000000', mr_date='20210811_101021', bad_channels = ['MEG0422', 'MEG0613', 'MEG1133', 'MEG2613']),
    dict(subject='0020', date='20210806_000000', mr_date='20210812_085148', bad_channels = ['MEG0422', 'MEG0811', 'MEG2613']),
    dict(subject='0021', date='20210806_000000', mr_date='20210811_145727', bad_channels = ['MEG0321', 'MEG0422', 'MEG0811', 'MEG2613']),
    dict(subject='0022', date='20210806_000000', mr_date='20210811_141117', bad_channels = ['MEG0422', 'MEG2613']),
    dict(subject='0023', date='20210809_000000', mr_date='20210812_112225', bad_channels = ['MEG0422', 'MEG1613']),
    dict(subject='0024', date='20210809_000000', mr_date='20210812_125146', bad_channels = ['MEG0422', 'MEG2613']),
    dict(subject='0026', date='20210810_000000', mr_date='20210811_120947', bad_channels = ['MEG0422', 'MEG2613']),
    dict(subject='0027', date='20210810_000000', mr_date='20210811_105000', bad_channels = ['MEG0232', 'MEG0422', 'MEG2613']),
    dict(subject='0028', date='20210817_000000', mr_date='20210820_111354', bad_channels = ['ECG003', 'MEG0422', 'MEG2613']),
    dict(subject='0029', date='20210817_000000', mr_date='20210820_103315', bad_channels = ['MEG0422', 'MEG0921', 'MEG1431', 'MEG2613']),
    dict(subject='0030', date='20210817_000000', mr_date='20210820_085929', bad_channels = ['MEG0422', 'MEG1643', 'MEG2613']),
    dict(subject='0031', date='20210825_000000', mr_date='20210820_094714', bad_channels = ['MEG0422', 'MEG1423', 'MEG2613'])
    ]
