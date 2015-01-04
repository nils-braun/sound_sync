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
	Server() : m_socketList(), m_bufferList(), m_frameRate(0), m_waitingTime(0), m_soundDataSize(0), m_soundBufferSize(0), m_startTime(0), m_senderIsConnected(false) {}

	void startListening() {
		startListeningSteppwise();
		while(true)
			mainLoop();
	}
	void startListeningSteppwise();
	void mainLoop();

	unsigned int getFrameRate() const { return m_frameRate; }
	unsigned int getWaitingTime() const { return m_waitingTime; }
	unsigned int getSoundDataSize() const { return m_soundDataSize; }
	unsigned int getSoundBufferSize() const { return m_soundBufferSize; }

	std::vector<Socket>::size_type size() { return(m_socketList.size()); }

private:
	SocketList m_socketList;
	BufferList m_bufferList;
	unsigned int m_frameRate;
	unsigned int m_waitingTime;
	unsigned int m_soundDataSize;
	unsigned int m_soundBufferSize;
	int m_startTime;

	bool m_senderIsConnected;

	void handleNewClientMessage(Socket & client);
	void handleNewSender(Socket& client, const pugi::xml_node & rootNode);
	void handleNewListener(Socket& client, const pugi::xml_node & rootNode);
	void handleNewUndefiniedClient(Socket& client);

	void sendNextBuffer();

	void setSoundBufferSize() {
		m_soundBufferSize = static_cast<unsigned int>(m_soundDataSize * m_waitingTime / 1000.0 * m_frameRate);
	}

	void handleNewSenderMessage(const Socket& client);
	void killClient(const Socket& client);
	void handleNewListenerMessage(Socket& client);
	void handleNewInvalidMessage(Socket& client);
	pugi::xml_node parseHelloMessage(const pugi::xml_document & document);
};
