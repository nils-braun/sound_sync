/*
 * FileDescriptorSet.cpp
 *
 *  Created on: 02.01.2015
 *      Author: nils
 */

#include "FileDescriptorSet.h"

void FileDescriptorSet::addSocket(const int socket) {
	if (socket > m_maximumFileDescriptorValue)
		m_maximumFileDescriptorValue = socket;
	FD_SET(socket, &m_internalFileDescriptorSet);
}

void FileDescriptorSet::addSocketList(const SocketList & socketList) {
	for(const Socket & socket : socketList) {
		addSocket(socket.getInternalFileDescriptor());
	}
}
