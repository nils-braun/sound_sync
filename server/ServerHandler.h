/*
 * ServerHandler.h
 *
 *  Created on: 29.12.2014
 *      Author: nils
 */

#pragma once

#include <sys/select.h>
#include <unistd.h>
#include <vector>
#include <algorithm>
#include <iostream>

class ServerHandler {

	typedef int Socket;
	typedef std::vector<Socket> SocketList;

public:
	static const int PORT = 50007;
	static const int START_BUFFER_SIZE = 1024;

	ServerHandler() : m_serverSocket(0), m_socketList(), m_fds(nullptr) {
		m_socketList.clear();
		m_socketList.reserve(4);

		m_fds = new fd_set;

		startServer();
	}
	virtual ~ServerHandler() {
		if(m_serverSocket != 0) {
			close(m_serverSocket);
		}

		delete m_fds;
	}

	void startListening();

private:
	void startServer();
	void mainloop();

	int fillFDSet() const;
	void addSocketToFDSet(const Socket& socket) const;
	void handlerSelectedSocket(const Socket& socket);

	void removeSocket(const Socket & deletedSocket) {
		auto iterator = std::find(m_socketList.begin(), m_socketList.end(), deletedSocket);
		m_socketList.erase(iterator);
	}

	void handleIncomingMessage(char * messageBuffer, const Socket & selectedSocket) { std::cout << messageBuffer << std::endl; }

	Socket m_serverSocket;
	SocketList m_socketList;

	fd_set * m_fds;
};
