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

void Server::handleNewSender(Socket& client, const pugi::xml_node & rootNode) {
	std::cout << "Registering new sender." << std::endl;
	client.setSocketType(Socket::SocketType::SenderType);

	pugi::xml_node optionsNode = rootNode.first_child();

	m_frameRate = std::atoi(optionsNode.attribute("frameRate").value());
	m_waitingTime = std::atoi(optionsNode.attribute("waitingTime").value());

	setSoundBufferSize();
	m_senderIsConnected = true;

	std::cout << "Added new sender with waitingTime " << m_waitingTime << " and frameRate " << m_frameRate << " resulting in " << m_soundBufferSize << std::endl;
}

void Server::handleNewListener(Socket& client, const pugi::xml_node &) {
	std::cout << "Registering new listener." << std::endl;
	client.setSocketType(Socket::SocketType::ListenerType);

	/*if(not m_senderIsConnected) {
		std::cout << "No sender connected." << std::endl;
		killClient(client);
		return;
	}*/

	pugi::xml_document document;
	pugi::xml_node rootNode = document.append_child("options");
	rootNode.append_attribute("frameRate").set_value(std::to_string(m_frameRate).c_str());
	rootNode.append_attribute("waitingTime").set_value(std::to_string(m_waitingTime).c_str());
	rootNode.append_attribute("startTime").set_value(std::to_string(0).c_str());

	std::stringstream stream;
	document.save(stream);

	sendMessage(client, stream.str());

	std::cout << "Added new listener." << std::endl;
}

void Server::killClient(Socket& client) {
	m_socketList.removeSocket(client);
	client.closeIt();
}

void Server::handleNewUndefiniedClient(Socket& client) {
	std::string incomingMessage = receiveMessage(client);

	pugi::xml_document document;
	pugi::xml_parse_result result = document.load_buffer(incomingMessage.c_str(), incomingMessage.size());

	if(result.status != pugi::xml_parse_status::status_ok) {
		std::cerr << "Client message can not be parsed." << std::endl;
		killClient(client);
		return;
	}

	pugi::xml_node rootNode = document.first_child();

	if (std::string("sender").compare(rootNode.attribute("type").value()) == 0) {
		handleNewSender(client, rootNode);
	} else if (std::string("receiver").compare(rootNode.attribute("type").value()) == 0) {
		handleNewListener(client, rootNode);
	} else {
		std::cerr << "[Error] Client type is not supported:" << incomingMessage << std::endl;
		killClient(client);
		return;
	}
}

void Server::handleNewSenderMessage(Socket& client) {
	try {
		Server::Buffer buffer = receiveBufferExact(client, m_soundBufferSize);
	}
	catch(const ClientClosedException & e) {
		std::cout << "Sender closing." << std::endl;
		m_senderIsConnected = false;
		killClient(client);
	}

	// TODO: Add buffer
}

void Server::handleNewClientMessage(Socket & client) {
	switch(client.getSocketType()) {
	case SocketType::UndefinedClientType:
		handleNewUndefiniedClient(client);
		break;
	case SocketType::SenderType:
		handleNewSenderMessage(client);
		break;
	case InvalidType:
	case ListenerType:
	default:
		std::cerr << "Do not understand client." << std::endl;
		killClient(client);
	}
}
