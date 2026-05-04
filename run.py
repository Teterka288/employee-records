from server import create_app

if __name__ == '__main__':
    PORT = 8000
    print(f'Сервер запущен: http://localhost:{PORT}')
    print('Для остановки нажмите Ctrl+C')
    
    server = create_app(PORT)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nСервер остановлен')
        server.server_close()