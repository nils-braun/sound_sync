/*
 * Server.h
 *
 *  Created on: 02.01.2015
 *      Author: nils
 */

#pragma once

#include "Socket.h"
#include "SocketList.h"
#include <iostream>

class Server: public Socket {
public:
	static const int PORT = 50007; // TODO: Read from file!

	Server();
	~Server() {
		closeIt();
	}

	void startListening() {
		startListeningSteppwise();
		while(true)
			mainLoop();
	}
	void startListeningSteppwise();
	void mainLoop();

	std::vector<Socket>::size_type size() { return(m_socketList.size()); }

private:
	SocketList m_socketList;

	void bindToPort();
};
