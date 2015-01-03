/*
 * ServerBase.cpp
 *
 *  Created on: 03.01.2015
 *      Author: nils
 */

#include "ServerBase.h"

void ServerBase::bindToPort() {
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


std::string ServerBase::receiveMessage(const Socket & socket, const int bufferSize) {
	char buffer[bufferSize];
	int numberOfReadBytes = recv(socket.getInternalFileDescriptor(), buffer, bufferSize, 0);
	if(numberOfReadBytes > 0) {
		return(std::string(buffer).substr(0, numberOfReadBytes));
	}
	else if (numberOfReadBytes == 0)
		throw clientClosedException;
	else
		throw messageReceiveException;
}

ServerBase::Buffer ServerBase::receiveBufferExact(const Socket & socket, const int bufferSize) {
	char * buffer = new char[bufferSize];
	int bytesReceivedSoFar = 0;

	while(bytesReceivedSoFar < bufferSize) {
		int numberOfReadBytes = recv(socket.getInternalFileDescriptor(), &buffer[bytesReceivedSoFar], bufferSize - bytesReceivedSoFar, 0);
		if(numberOfReadBytes > 0) {
			bytesReceivedSoFar += numberOfReadBytes;
		}
		else if (numberOfReadBytes == 0)
			throw clientClosedException;
		else
			throw messageReceiveException;
	}

	return(ServerBase::Buffer(buffer, bufferSize));
}

void ServerBase::sendMessage(const Socket & socket, const std::string & message) {
	write(socket.getInternalFileDescriptor(), message.c_str(), message.size());
}

void ServerBase::sendBuffer(const Socket & socket, const ServerBase::Buffer & buffer) {
	write(socket.getInternalFileDescriptor(), buffer.first, buffer.second);
}
