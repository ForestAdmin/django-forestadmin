APIMAP_ERRORS = {
    404: {
        'level': 'error',
        'message': 'Cannot find the project related to the envSecret you configured. Can you check on Forest that you copied it properly in the Forest settings?'  # noqa E501
    },
    503: {
        'level': 'warning',
        'message': 'Forest is in maintenance for a few minutes. We are upgrading your experience in the forest. We just need a few more minutes to get it right.'  # noqa E501
    },
    'error': {
        'level': 'error',
        'message': 'An error occured with the apimap sent to Forest. Please contact support@forestadmin.com for further investigations.'  # noqa E501
    }
}
