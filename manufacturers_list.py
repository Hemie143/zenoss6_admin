import zenAPI.zenApiLib
import argparse
from openpyxl import Workbook

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Manage Manufacturers')
    parser.add_argument('-s', dest='environ', action='store', default='z6_prod')
    # parser.add_argument('-f', dest='filename', action='store', default='local_templates.xlsx')
    options = parser.parse_args()
    environ = options.environ
    # filename = options.filename

    wb = Workbook()
    filename = 'manufacturers_export.xlsx'
    ws = wb.active
    ws.title = 'Products'

    ws.append(['Manufacturer', 'Product', 'Type', 'Keys'])


    # Routers
    mr = zenAPI.zenApiLib.zenConnector(section=environ, routerName='ManufacturersRouter')

    result = mr.callMethod('getManufacturerList')['result']
    data = result['data']
    for manufacturer in data:
        m_uid = manufacturer['uid']
        m_data = mr.callMethod('getManufacturerData', uid=m_uid)['result']['data']
        if len(m_data) > 1:
            print('More data than expected: {}'.format(m_data))
        else:
            m_data = m_data[0]
        # print(m_data)
        m_label = m_data['id']
        m_products = mr.callMethod('getProductsByManufacturer', uid=m_uid)['result']['data']
        # [{u'count': 145, u'type': u'Hardware', u'id': u'VMware Virtual disk SCSI Disk Device',
        # u'key': [u'VMware Virtual disk SCSI Disk Device'],
        # u'uid': u'/zport/dmd/Manufacturers/(Standard disk drives)/products/VMware Virtual disk SCSI Disk Device'}]

        for p in m_products:
            # print(p)
            # p_data = mr.callMethod('getProductData', uid=p['uid'], prodname=p['id'])['result']['data']
            # print(p_data)
            row = [m_label, p['id'], p['type']]
            ws.append(row)

    wb.save(filename=filename)