/*
 * Socket.h
 *
 *  Created on: 01.01.2015
 *      Author: nils
 */

#pragma once

#include <errno.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <cstring>
#include <iostream>
#include <unistd.h>

#include "Exceptions.h"


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
	Socket(const int internalFileDescriptor) : m_socketType(SocketType::InvalidType),
	m_socketAddress(), m_internalFileDescriptor(internalFileDescriptor) { }

	Socket() : Socket(0) { };

	int getInternalFileDescriptor() const {
		return(m_internalFileDescriptor);
	}

	SocketType getSocketType() const {
		return(m_socketType);
	}

	void setSocketType(SocketType socketType) {
		m_socketType = socketType;
	}

	struct in_addr getSocketIPAddress() const {
		return(m_socketAddress.sin_addr);
	}

	int getSocketIPPort() const {
		return(m_socketAddress.sin_port);
	}

	void acceptFromServer(const Socket & server) {
		socklen_t dummySize = sizeof(m_socketAddress);
		int newClient = accept(server, reinterpret_cast<struct sockaddr*>(&m_socketAddress), &dummySize);
		if(newClient == -1) {
			std::cerr << "Error while accepting client from " << std::to_string(static_cast<int>(server)) <<
					": " << strerror(errno) << std::endl;
			throw clientAcceptException;
		}
		else {
			m_internalFileDescriptor = newClient;
			m_socketType = SocketType::UndefinedClientType;
		}
	}

	operator int() const {
		return(m_internalFileDescriptor);
	}

	bool operator==(const Socket & rhs) const {
		return(rhs.m_internalFileDescriptor == m_internalFileDescriptor);
	}

	void closeIt() const {
		close(m_internalFileDescriptor);
	}

private:
	SocketType m_socketType;
	struct sockaddr_in m_socketAddress;
	int m_internalFileDescriptor;
};


