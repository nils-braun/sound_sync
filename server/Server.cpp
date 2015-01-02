/*
 * Server.cpp
 *
 *  Created on: 02.01.2015
 *      Author: nils
 */

#include "Server.h"
#include <sys/socket.h>
#include <sys/select.h>

Server::Server() : Socket(socket(PF_INET, SOCK_STREAM, 0)) {
	bindToPort();
}

void Server::bindToPort() {
	int option = 1;
	setsockopt(getInternalFileDescriptor(), SOL_SOCKET, SO_REUSEADDR, &option, sizeof(option));
	if(getInternalFileDescriptor() == -1) {
		throw serverStartException;
	}

	struct sockaddr_in serverAddress;
	serverAddress.sin_addr.s_addr = INADDR_ANY;
	serverAddress.sin_port = htons(PORT);
	serverAddress.sin_family = AF_INET;

	int returnValue = bind(getInternalFileDescriptor(), reinterpret_cast<struct sockaddr*>(&serverAddress), sizeof(serverAddress));

	if(returnValue == -1) {
		throw serverBindException;
	}
}

void Server::startListeningSteppwise() {
	int returnValue = listen(getInternalFileDescriptor(), 5);

	if(returnValue == -1) {
		throw serverListenException;
	}
}

void Server::mainLoop() {
	fd_set fileDescriptorSet;
	FD_ZERO(&fileDescriptorSet);

	int maximumValue = 0;
	for(const Socket & socket : m_socketList) {
		int currentFileDescriptor = socket.getInternalFileDescriptor();
		if(currentFileDescriptor > maximumValue)
			maximumValue = currentFileDescriptor;
		FD_SET(currentFileDescriptor, &fileDescriptorSet);
	}

	// Add the server itself
	int currentFileDescriptor = getInternalFileDescriptor();
	if(currentFileDescriptor > maximumValue)
		maximumValue = currentFileDescriptor;
	FD_SET(currentFileDescriptor, &fileDescriptorSet);

	select(maximumValue + 1, &fileDescriptorSet, nullptr, nullptr, nullptr);

	if(FD_ISSET(getInternalFileDescriptor(), &fileDescriptorSet)) {
		m_socketList.acceptFromServer(getInternalFileDescriptor());
	}
	// Find the sender and start reading!
}
