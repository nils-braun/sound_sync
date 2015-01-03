/*
 * ServerBase.h
 *
 *  Created on: 03.01.2015
 *      Author: nils
 */

#pragma once

#include "Socket.h"
#include <string>

class ServerBase : public Socket {
public:
	static const int PORT = 50007; // TODO: Read from file!

	typedef std::pair<char*, int> Buffer;

	ServerBase() : Socket(socket(PF_INET, SOCK_STREAM, 0)) {
		bindToPort();
	}
	virtual ~ServerBase() {
		closeIt();
	}

protected:
	void bindToPort();
	std::string receiveMessage(const Socket & socket, const int bufferSize = 1024);
	Buffer receiveBufferExact(const Socket & socket, const int bufferSize);
	void sendMessage(const Socket & socket, const std::string & message);
	void sendBuffer(const Socket & socket, const ServerBase::Buffer & buffer);
};
