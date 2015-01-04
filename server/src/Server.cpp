/*
 * Server.cpp
 *
 *  Created on: 02.01.2015
 *      Author: nils
 */

#include "Server.h"
#include <sys/socket.h>
#include <sys/select.h>
#include "FileDescriptorSet.h"
#include <sstream>
#include <time.h>

void Server::startListeningSteppwise() {
	int returnValue = listen(getInternalFileDescriptor(), 5);

	if(returnValue == -1) {
		throw serverListenException;
	}
}

void Server::mainLoop() {
	FileDescriptorSet fileDescriptorSet;
	fileDescriptorSet.clear();

	fileDescriptorSet.addSocketList(m_socketList);
	fileDescriptorSet.addSocket(getInternalFileDescriptor());

	fileDescriptorSet.startSelect();

	if(fileDescriptorSet.isReadable(getInternalFileDescriptor())) {
		m_socketList.acceptFromServer(getInternalFileDescriptor());
	}
	for(Socket & socket : m_socketList) {
		if(fileDescriptorSet.isReadable(socket.getInternalFileDescriptor())) {
			handleNewClientMessage(socket);
		}
	}
}

void Server::handleNewClientMessage(Socket & client) {
	switch(client.getSocketType()) {
	case SocketType::UndefinedClientType:
		handleNewUndefiniedClient(client);
		return;
	case SocketType::SenderType:
		handleNewSenderMessage(client);
		return;
	case ListenerType:
		handleNewListenerMessage(client);
		return;
	case InvalidType:
	default:
		handleNewInvalidMessage(client);
		return;
	}
}

void Server::handleNewUndefiniedClient(Socket& client) {
	std::string incomingMessage = receiveMessage(client);
	pugi::xml_document document;
	pugi::xml_parse_result result = document.load_buffer(incomingMessage.c_str(), incomingMessage.size());
	if (result.status != pugi::xml_parse_status::status_ok) {
		std::cerr << "Can not parse client welcome message: " << incomingMessage << " " << result.description() << std::endl;
		killClient(client);
		return;
	}
	pugi::xml_node rootNode = document.first_child();

	if (std::string("sender") == rootNode.attribute("type").value()) {
		handleNewSender(client, rootNode);
	} else if (std::string("receiver") == rootNode.attribute("type").value()) {
		handleNewListener(client, rootNode);
	} else {
		std::cerr << "[ERROR] Undefined client type is not supported: " << incomingMessage << std::endl;
		killClient(client);
	}
}

void Server::handleNewSender(Socket& client, const pugi::xml_node & rootNode) {
	client.setSocketType(Socket::SocketType::SenderType);

	pugi::xml_node optionsNode = rootNode.first_child();

	m_frameRate = std::atoi(optionsNode.attribute("frameRate").value());
	m_waitingTime = std::atoi(optionsNode.attribute("waitingTime").value());
	m_soundDataSize = std::atoi(optionsNode.attribute("soundDataSize").value());
	m_startTime = time(nullptr);

	setSoundBufferSize();
	m_senderIsConnected = true;

	std::cout << "[INFO] Added new sender with waitingTime " << m_waitingTime << ", frameRate " << m_frameRate << " and soundDataSize " <<
			m_soundDataSize << " resulting in " << m_soundBufferSize << std::endl;
}

void Server::handleNewListener(Socket& client, const pugi::xml_node &) {
	client.setSocketType(Socket::SocketType::ListenerType);

	if(not m_senderIsConnected) {
		std::cerr << "[ERROR] No sender connected." << std::endl;
		killClient(client);
		return;
	}

	pugi::xml_document document;
	pugi::xml_node rootNode = document.append_child("options");
	rootNode.append_attribute("frameRate").set_value(std::to_string(m_frameRate).c_str());
	rootNode.append_attribute("waitingTime").set_value(std::to_string(m_waitingTime).c_str());
	rootNode.append_attribute("soundDataSize").set_value(std::to_string(m_soundDataSize).c_str());
	// TODO: Calculate correct start time!
	rootNode.append_attribute("startTime").set_value(std::to_string(m_startTime).c_str());

	std::stringstream stream;
	document.save(stream);

	sendMessage(client, stream.str());

	std::cout << "[INFO] Added new listener." << std::endl;
}

void Server::killClient(const Socket& client) {
	m_socketList.removeSocket(client);
	client.closeIt();
}

void Server::handleNewSenderMessage(const Socket& client) {
	try {
		Buffer buffer = receiveBufferExact(client, m_soundBufferSize);
		m_bufferList.add(buffer);
		sendNextBuffer();
	}
	catch(const ClientClosedException & e) {
		std::cout << "[INFO] Closing sender." << std::endl;
		m_senderIsConnected = false;
		killClient(client);
	}
}

void Server::sendNextBuffer() {
	for(Socket & listener : m_socketList) {
		if(listener.getSocketType() == Socket::SocketType::ListenerType) {
			int index = m_bufferList.getNumberOfBufferForClient(listener);
			while(index >= 0) {
				Buffer buffer = m_bufferList.returnBuffer(index);
				sendBuffer(listener, buffer);
				index = m_bufferList.getNumberOfBufferForClient(listener);
			}
		}
	}
}

void Server::handleNewListenerMessage(Socket& client) {
	// TODO: Handle real message from listener!
	std::cout << "[INFO] Closing listener." << std::endl;
	killClient(client);
}

void Server::handleNewInvalidMessage(Socket& client) {
	std::cerr << "[ERROR] Do not understand client." << std::endl;
	killClient(client);
}
