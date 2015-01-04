/*
 * FileDescriptorSet.h
 *
 *  Created on: 02.01.2015
 *      Author: nils
 */

#pragma once

#include <sys/select.h>
#include "Socket.h"
#include "SocketList.h"

class FileDescriptorSet {
public:
	FileDescriptorSet() : m_internalFileDescriptorSet(), m_maximumFileDescriptorValue(0) {
		clear();
	}

	void addSocket(const int socket);
	void addSocketList(const SocketList & socketList);
	void clear() {
		FD_ZERO(&m_internalFileDescriptorSet);
	}

	void startSelect() {
		select(m_maximumFileDescriptorValue + 1, &m_internalFileDescriptorSet, nullptr, nullptr, nullptr);
	}

	bool isReadable(const Socket & socket) { return(FD_ISSET(socket.getInternalFileDescriptor(), &m_internalFileDescriptorSet)); }

private:
	fd_set m_internalFileDescriptorSet;
	int m_maximumFileDescriptorValue;
};
