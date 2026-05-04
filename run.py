from server import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
    
    print(f'Сервер запущен: http://localhost:{PORT}')
    print('Для остановки нажмите Ctrl+C')
    
    server = create_app(PORT)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nСервер остановлен')
        server.server_close()