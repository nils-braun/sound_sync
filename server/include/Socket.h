/*
 * Socket.h
 *
 *  Created on: 01.01.2015
 *      Author: nils
 */

#pragma once

#include <errno.h>
#include <Exceptions.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>
#include <cstring>
#include <iostream>


class Socket {
public:
	enum SocketType {
		ServerType = 0,
		UndefinedClientType = 1,
		ListenerType = 2,
		SenderType = 3,
		InvalidType = 99
	};

public:
	/**
	 * Create a new socket. This class is a wrapper around the file-descriptor-like interface for accessing the sockets.
	 * It should be used instead of the ints. It also has some variables for storing various information for convenience.
	 */
	Socket(const int internalFileDescriptor) :
		m_socketType(SocketType::InvalidType),
		m_socketAddress(),
		m_internalFileDescriptor(internalFileDescriptor),
		m_bufferIndex(0) { }

	/**
	 * Return the internal file descriptor for accessing the low level socket stuff.
	 */
	int getInternalFileDescriptor() const {
		return(m_internalFileDescriptor);
	}

	/**
	 * Return the socket type. We differentiate between server and client. For the client there are more options. See SocketType.
	 */
	SocketType getSocketType() const {
		return(m_socketType);
	}

	/**
	 * Set the socket type.
	 */
	void setSocketType(SocketType socketType) {
		m_socketType = socketType;
	}

	/**
	 * Return the IP address of this socket. Is used for testing purposes.
	 */
	struct in_addr getSocketIPAddress() const {
		return(m_socketAddress.sin_addr);
	}

	/**
	 * Return the IP port of the socket. Is used for testing purposes.
	 */
	int getSocketIPPort() const {
		return(m_socketAddress.sin_port);
	}

	/**
	 * Static method for creating the socket out of a pending server. Sets the variables coming from the server correctly.
	 * If something went wrong throws an exeption.
	 */
	static Socket acceptFromServer(const Socket & server) {
		struct sockaddr_in socketAddress;
		socklen_t dummySize = sizeof(socketAddress);
		int newClient = accept(server.getInternalFileDescriptor(), reinterpret_cast<struct sockaddr*>(&socketAddress), &dummySize);
		if(newClient == -1) {
			std::cerr << "Error while accepting client:" << strerror(errno) << std::endl;
			throw clientAcceptException;
		}
		else {
			Socket newSocket(newClient);
			newSocket.m_socketAddress = socketAddress;
			newSocket.setSocketType(SocketType::UndefinedClientType);
			return newSocket;
		}
	}

	/**
	 * This comparison is used when storing the sockets in a list.
	 */
	bool operator==(const Socket & rhs) const {
		return(rhs.m_internalFileDescriptor == m_internalFileDescriptor);
	}

	/**
	 * Close the under laying internal file descriptor. Should be executed every time the connection is closed.
	 * Attention: do not close a file descriptor if you want to reuse this connection! This is the reason why the close method
	 * is not implemented in the destructor.
	 * TODO: A resource handling class would be much better here..
	 */
	void closeIt() const {
		close(m_internalFileDescriptor);
	}

	/**
	 * Return the buffer index (only valid for clients). In this index we store the number of buffers read/written by this client.
	 */
	unsigned long int getBufferIndex() const {
		return m_bufferIndex;
	}

	/**
	 * Set the buffer index.
	 */
	void setBufferIndex(unsigned long int bufferIndex) {
		m_bufferIndex = bufferIndex;
	}

private:
	SocketType m_socketType; 					/**< The socket type.*/
	struct sockaddr_in m_socketAddress;			/**< The address of this socket. Only for testing */
	int m_internalFileDescriptor;				/**< The file descriptor this class wrappes around */
	unsigned long int m_bufferIndex;			/**< The buffer index */
};


