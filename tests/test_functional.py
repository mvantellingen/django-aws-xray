def test_dummy_view(client, xray_daemon):
    response = client.get('/')
    assert response.status_code == 200
    assert response.content == b'hello world'

    messages = xray_daemon.get_new_messages()
    assert len(messages) >= 1
