/*
 * Exceptions.h
 *
 *  Created on: 02.01.2015
 *      Author: nils
 */

#pragma once

#include <errno.h>
#include <exception>
#include <cstring>
#include <string>

class SocketError : public std::exception {
public:
	virtual const std::string m_preString() const = 0;
	virtual const char* what() const throw() {
		return((m_preString() + std::string(strerror(errno))).c_str());
	}
};

extern class ClientAcceptException : public SocketError {
	const std::string m_preString() const {
		return("Exception in client accept: ");
	}
} clientAcceptException;

extern class SocketLookupException : public SocketError {
	const std::string m_preString() const {
		return("Socket not in list: ");
	}
} socketLookupException;

extern class ServerBindException : public SocketError {
	const std::string m_preString() const {
		return("Error while binding: ");
	}
} serverBindException;

extern class ServerListenException : public SocketError {
	const std::string m_preString() const {
		return("Error while listening: ");
	}
} serverListenException;

extern class ServerStartException : public SocketError {
	const std::string m_preString() const {
		return("Error while starting server: ");
	}
} serverStartException;
