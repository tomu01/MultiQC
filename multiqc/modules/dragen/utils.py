from collections import OrderedDict


from multiqc import config


read_format = '{:,.1f}'
if config.read_count_multiplier == 1:
    read_format = '{:,.0f}'
read_format += '&nbsp;' + config.read_count_prefix

base_format = '{:,.1f}&nbsp;'
if config.base_count_multiplier == 1:
    base_format = '{:,.0f}'
elif config.base_count_multiplier == 0.000000001:
    base_format = '{:,.2f}'
base_format += '&nbsp;' + config.base_count_prefix


class Metric:
    def __init__(self, id, title, in_genstats=None, in_own_tabl=None, unit=None,
                 descr=None, fmt=None, modify=None, namespace=None):
        self.id = id
        self.title = title
        self.unit = unit
        self.in_genstats = in_genstats
        self.in_own_tabl = in_own_tabl
        self.descr = descr
        self.fmt = fmt
        self.modify = modify
        self.namespace = namespace


def make_headers(parsed_metric_ids, metrics):
    # Init general stats table
    genstats_headers = OrderedDict()

    # Init headers for an own separate table
    own_tabl_headers = OrderedDict()

    for metric in metrics:
        col = dict(
            title=metric.title,
            description=metric.descr,
            min=0,
        )

        # choosing color based on metric namespace, guessing namespace by unit
        if metric.unit == 'reads':
            col['scale'] = 'Greens'
        elif metric.unit == 'bases':
            col['scale'] = 'Blues'
        elif metric.unit == 'bp':
            col['scale'] = 'Reds'
        elif metric.unit == 'x' or metric.namespace == 'Coverage':
            col['scale'] = 'Oranges'
        elif metric.namespace == 'Variants':
            col['scale'] = 'Purples'

        if metric.id + ' pct' in parsed_metric_ids:
            # if % value is available, showing it instead of the number value; the number value will be hidden
            pct_col = dict(
                col,
                description=metric.descr.replace(', {}', '').replace('Number of ', '% of '),
                max=100,
                suffix='%',
            )
            if metric.in_genstats is not None:
                show = metric.in_genstats == '%'
                genstats_headers[metric.id + ' pct'] = dict(pct_col, hidden=not show)
            if metric.in_own_tabl is not None:
                show = metric.in_own_tabl == '%'
                own_tabl_headers[metric.id + ' pct'] = dict(pct_col, hidden=not show)

        if metric.unit == 'reads':
            col['description'] = col['description'].format(config.read_count_desc)
            col['modify'] = lambda x: x * config.read_count_multiplier
            col['shared_key'] = 'read_count'
            col['format'] = read_format
        elif metric.unit == 'bases':
            col['description'] = col['description'].format(config.base_count_desc)
            col['modify'] = lambda x: x * config.base_count_multiplier
            col['shared_key'] = 'base_count'
            col['format'] = base_format
        elif metric.unit == 'len':
            col['suffix'] = ' bp'
            col['format'] = '{:,.0f}'
        elif metric.unit == 'x':
            col['suffix'] = ' x'
            col['format'] = '{:,.1f}'
        elif metric.unit == '%':
            col['suffix'] = ' %'
            col['format'] = '{:,.1f}'
        elif any(metric.descr.startswith(pref) for pref in ('Total number of ', 'The number of ', 'Number of ')):
            col['format'] = '{:,.0f}'

        if metric.in_genstats is not None:
            genstats_headers[metric.id] = dict(col, hidden=metric.in_genstats != '#')
        if metric.in_own_tabl is not None:
            own_tabl_headers[metric.id] = dict(col, hidden=metric.in_own_tabl != '#')

    return genstats_headers, own_tabl_headers
