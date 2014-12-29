/*
 * ServerHandler.cpp
 *
 *  Created on: 29.12.2014
 *      Author: nils
 */

#include "ServerHandler.h"

#include <netinet/in.h>
#include <sys/socket.h>
#include <exception>
#include <iostream>

class ServerException : public std::exception {
	virtual const char* what() const throw() {
		return("Error in Server!");
	}
} serverException;


void ServerHandler::startServer() {
	m_serverSocket = socket(PF_INET, SOCK_STREAM, 0);
	if (m_serverSocket == -1)
	{
		std::cerr << "socket() failed" << std::endl;
		throw serverException;
	}
}

void ServerHandler::startListening() {
	struct sockaddr_in addr;

	addr.sin_addr.s_addr = INADDR_ANY;
	addr.sin_port = htons(PORT);
	addr.sin_family = AF_INET;

    if (bind(m_serverSocket, (struct sockaddr*)&addr, sizeof(addr)) == -1)
    {
    	std::cerr << "bind() failed" << std::endl;;
        throw serverException;
    }

    if (listen(m_serverSocket, 3) == -1)
	{
		std::cerr << "listen() failed" << std::endl;
		throw serverException;
	}

    mainloop();
}

void ServerHandler::addSocketToFDSet(const Socket& socket) const {
	FD_SET(socket, m_fds);
}

int ServerHandler::fillFDSet() const {
    int max = 0;

    for (const Socket & socket : m_socketList) {
        if (socket < FD_SETSIZE) {
			addSocketToFDSet(socket);

            if (socket > max)
                max = socket;

        } else {
            std::cerr << "skipped client, socket too large!" << std::endl;
        }
    }

	addSocketToFDSet(m_serverSocket);

	if (static_cast<int>(m_serverSocket) > max)
		max = static_cast<int>(m_serverSocket);

    return(max);
}

void ServerHandler::mainloop() {
	for(;;)
	{
		FD_ZERO(m_fds);
		int max = fillFDSet();

		select(max + 1, m_fds, nullptr, nullptr, nullptr);

		for(const Socket & socketEntry : m_socketList) {
			if (FD_ISSET(socketEntry, m_fds)) {
				handlerSelectedSocket(socketEntry);
			}
		}

		if(FD_ISSET(m_serverSocket, m_fds)) {
			Socket newClient = accept(m_serverSocket, nullptr, 0);
			m_socketList.push_back(newClient);
			std::cout << "New client connected!" << std::endl;
		}
	}
}

void ServerHandler::handlerSelectedSocket(const Socket& selectedSocket) {
	char messageBuffer[START_BUFFER_SIZE];
	int bytesRead = read(selectedSocket, messageBuffer, sizeof(messageBuffer));
	if (bytesRead == 0)
		removeSocket(selectedSocket);
	else
		handleIncomingMessage(messageBuffer, selectedSocket);
}
