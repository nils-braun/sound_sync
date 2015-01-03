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
#include <array>
#include <pugixml.hpp>
#include "ServerBase.h"

class Server: public ServerBase {
public:
	Server() : m_frameRate(0), m_waitingTime(0), m_soundBufferSize(0), m_senderIsConnected(false) {}

	void startListening() {
		startListeningSteppwise();
		while(true)
			mainLoop();
	}
	void startListeningSteppwise();
	void mainLoop();

	int getFrameRate() const { return m_frameRate; }
	int getWaitingTime() const { return m_waitingTime; }

	std::vector<Socket>::size_type size() { return(m_socketList.size()); }

private:
	SocketList m_socketList;
	unsigned int m_frameRate;
	unsigned int m_waitingTime;
	unsigned int m_soundBufferSize;

	bool m_senderIsConnected;

	void handleNewClientMessage(Socket & client);
	void handleNewSender(Socket& client, const pugi::xml_node & rootNode);
	void handleNewListener(Socket& client, const pugi::xml_node & rootNode);
	void handleNewUndefiniedClient(Socket& client);

	void setSoundBufferSize() {
		m_soundBufferSize = int(4.0 * m_waitingTime / 1000.0 * m_frameRate);
	}

	void handleNewSenderMessage(Socket& client);
	void killClient(Socket& client);
};
