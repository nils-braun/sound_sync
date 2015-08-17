/*
 * ServerBase.h
 *
 *  Created on: 03.01.2015
 *      Author: nils
 */

#pragma once

#include "Socket.h"
#include "BufferList.h"
#include <string>

class ServerBase : public Socket {
public:
	static const int PORT = 50007; // TODO: Read from file!

	/**
	 * Create a new server. This class provides access to the base server activities like sending a message,
	 * sending a buffer or receiving a message/buffer from the socket.
	 */
	ServerBase() : Socket(socket(PF_INET, SOCK_STREAM, 0)) {
		bindToPort();
	}

	/**
	 * Close the server and the corresponding file descriptor.
	 */
	virtual ~ServerBase() {
		closeIt();
	}

protected:
	/**
	 * Receive a message with the given buffer size. The message can be smaller than the message size.
	 */
	std::string receiveMessage(const Socket & socket, const int bufferSize = 1024);

	/**
	 * Receive a buffer with the given buffer size. The returned buffer has exactly the given size. Blocks until the buffer is full.
	 */
	Buffer receiveBufferExact(const Socket & socket, const int bufferSize);

	/**
	 * Send a message. Does not block.
	 */
	void sendMessage(const Socket & socket, const std::string & message);

	/**
	 * Send a buffer. Blocks until the buffer is send.
	 */
	void sendBuffer(const Socket & socket, const Buffer & buffer);

private:
	/**
	 * Bind the file descriptor to the standard port.
	 */
	void bindToPort();

private:
	const int BUFFER_SIZE_OF_BUFFER_INDEX = 8;
};
