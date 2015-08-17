/*
 * SocketList.h
 *
 *  Created on: 02.01.2015
 *      Author: nils
 */

#pragma once

#include <algorithm>
#include <iterator>
#include <vector>

#include <memory>

#include "Exceptions.h"
#include "Socket.h"

class SocketList {
public:
	/**
	 * Create a socket list. This class is a wrapper around a std::vector for storing the clients connected to a server.
	 * TODO: Maybe implement a map here?
	 */
	SocketList() : m_internalList() { }

	/**
	 * Close all connected clients.
	 */
	~SocketList() {
		for(const Socket &socket : m_internalList) {
			socket.closeIt();
		}
	}

	/**
	 * Accept a new socket from the server and add it to the list.
	 */
	void acceptFromServer(const Socket & server) {
		Socket newClientSocket = Socket::acceptFromServer(server);
		m_internalList.push_back(newClientSocket);
	}

	/**
	 * Remove a given client from the list.
	 */
	void removeSocket(const Socket & socketToBeRemoved) {
		std::vector<Socket>::iterator socketPosition = std::find(begin(), end(), socketToBeRemoved);
		if(socketPosition == end()) {
			throw socketLookupException;
		}
		else {
			m_internalList.erase(socketPosition);
		}
	}

	/**
	 * Convenience things from std::vector reimplemented.
	 */
	std::vector<Socket>::size_type size() const { return(m_internalList.size()); }
	std::vector<Socket>::const_iterator begin() const { return(m_internalList.begin()); }
	std::vector<Socket>::const_iterator end() const { return(m_internalList.end()); }
	std::vector<Socket>::iterator begin() { return(m_internalList.begin()); }
	std::vector<Socket>::iterator end() { return(m_internalList.end()); }

private:
	std::vector<Socket> m_internalList; 	/**< The internal vector with the client. */
};
