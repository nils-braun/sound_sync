/*
 * ServerBase.cpp
 *
 *  Created on: 03.01.2015
 *      Author: nils
 */

#include "ServerBase.h"
#include <memory>
#include <array>

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

Buffer ServerBase::receiveBufferExact(const Socket & socket, const int bufferSize) {
	Buffer::bufferContentType * buffer = new Buffer::bufferContentType[bufferSize];
	int bytesReceivedSoFar = 0;

	while(bytesReceivedSoFar < bufferSize) {
		int numberOfReadBytes = recv(socket.getInternalFileDescriptor(), &buffer[bytesReceivedSoFar], bufferSize - bytesReceivedSoFar, 0);
		if(numberOfReadBytes > 0) {
			bytesReceivedSoFar += numberOfReadBytes;
		}
		else if (numberOfReadBytes == 0) {
			delete[] buffer;
			throw clientClosedException;
		}
		else {
			delete[] buffer;
			throw messageReceiveException;
		}
	}

	return(Buffer(buffer, bufferSize, 0));
}

void ServerBase::sendMessage(const Socket & socket, const std::string & message) {
	write(socket.getInternalFileDescriptor(), message.c_str(), message.size());
}

void ServerBase::sendBuffer(const Socket & socket, const Buffer & buffer) {
	int bufferNumber = buffer.getBufferNumber();
	char sendBuffer[buffer.getSize() + sizeof(bufferNumber)];
	std::copy(reinterpret_cast<const char*>(&bufferNumber), reinterpret_cast<const char*>(&bufferNumber) + sizeof(bufferNumber), sendBuffer);
	std::copy(buffer.getBuffer(), buffer.getBuffer() + buffer.getSize(), &sendBuffer[sizeof(bufferNumber)]);
	write(socket.getInternalFileDescriptor(), sendBuffer, sizeof(sendBuffer));
}
