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

#include "Exceptions.h"
#include "Socket.h"

class SocketList {
public:
	SocketList() : m_internalList() { }

	~SocketList() {
		for(const Socket &socket : m_internalList) {
			socket.closeIt();
		}
	}

	void acceptFromServer(const Socket & server) {
		Socket newClientSocket;
		newClientSocket.acceptFromServer(server);
		m_internalList.push_back(newClientSocket);
	}

	void removeSocket(const Socket & socketToBeRemoved) {
		std::vector<Socket>::iterator socketPosition = std::find(begin(), end(), socketToBeRemoved);
		if(socketPosition == end()) {
			throw socketLookupException;
		}
		else {
			m_internalList.erase(socketPosition);
		}
	}

	std::vector<Socket>::size_type size() { return(m_internalList.size()); }
	std::vector<Socket>::iterator begin() { return(m_internalList.begin()); }
	std::vector<Socket>::iterator end() { return(m_internalList.end()); }

private:
	std::vector<Socket> m_internalList;
};
