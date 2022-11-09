fk_mapping_test_data = [
    (False, {'type': 'integer'}),
    (True, {'type': {
        'properties': {
            'id': {'type': 'integer'},
            'username': {'type': 'text'},
            'is_active': {'type': 'boolean'},
            'age': {'type': 'short'},
        },
    }}),
]
