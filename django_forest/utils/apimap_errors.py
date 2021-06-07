APIMAP_ERRORS = {
    0: {
        'level': 'warning',
        'message': 'Cannot send the apimap to Forest. Are you online?'
    },
    404: {
        'level': 'error',
        'message': 'Cannot find the project related to the envSecret you configured. Can you check on Forest that you copied it properly in the Forest initialization?'  # noqa E501
    },
    503: {
        'level': 'warning',
        'message': 'Forest is in maintenance for a few minutes. We are upgrading your experience in the forest. We just need a few more minutes to get it right.'  # noqa E501
    },
}
