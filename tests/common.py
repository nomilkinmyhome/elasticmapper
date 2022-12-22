fk_mapping_test_data = [
    (False, {'type': 'text'}),
    (True, {'type': {
        'properties': {
            'id': {'type': 'text'},
            'username': {'type': 'text'},
            'is_active': {'type': 'boolean'},
            'age': {'type': 'short'},
        },
    }}),
]
