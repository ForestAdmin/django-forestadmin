from datetime import datetime

from django.http import HttpResponse


class CsvMixin:
    def get_related_res(self, data, value):
        related_res = None
        if value['data'] is not None:
            related_res = next((x for x in data['included']
                                if x['type'] == value['data']['type'] and str(x['id']) == str(value['data']['id'])),
                               None)
        return related_res

    def fill_csv_relationships(self, res, record, data, params):
        for name, value in record['relationships'].items():
            related_res = self.get_related_res(data, value)
            if related_res:
                if 'attributes' in related_res:
                    res[name] = related_res['attributes'][params[f'fields[{name}]']]
                else:
                    res[name] = related_res['id']
        return res

    def fill_csv(self, data, writer, params):
        for record in data['data']:
            res = record['attributes']
            res['id'] = record[self.Model._meta.pk.name]
            if 'relationships' in record and 'included' in data:
                res = self.fill_csv_relationships(res, record, data, params)

            writer.writerow(res)

    def csv_response(self, csv_filename):
        return HttpResponse(
            content_type='text/csv; charset=utf-8',
            headers={
                'Content-Disposition': f'attachment; filename="{csv_filename}.csv"',
                'Last-Modified': datetime.now(),
                'X-Accel-Buffering': 'no',
                'Cache-Control': 'no-cache'
            },
        )
