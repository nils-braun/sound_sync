/*
 * BufferList.h
 *
 *  Created on: 03.01.2015
 *      Author: nils
 */

#pragma once

#include <deque>
#include <memory>
#include <array>
#include "Socket.h"
#include "Exceptions.h"

class Buffer {
public:
	typedef unsigned char bufferContentType;

	Buffer() = delete;

	Buffer(const bufferContentType* const buffer, const int size, const int bufferNumber) :
		m_buffer(sharedBufferPointer(buffer, [](const bufferContentType * const buffer) { delete[] buffer; })),
			m_size(size), m_bufferNumber(bufferNumber) {}

	int getSize() const { return m_size; }
	const bufferContentType * getBuffer() const { return m_buffer.get(); }

	int getBufferNumber() const {
		return m_bufferNumber;
	}

	void setBufferNumber(int bufferNumber) {
		m_bufferNumber = bufferNumber;
	}

private:
	typedef std::shared_ptr<const bufferContentType> sharedBufferPointer;
	sharedBufferPointer m_buffer;
	int m_size;
	int m_bufferNumber;
};

class BufferList {
public:
	BufferList() : m_numberOfFirstBuffer(0), m_internalBufferList() {}

	void add(Buffer & buffer) {
		m_internalBufferList.push_back(buffer);
		m_internalBufferList.back().setBufferNumber(getMaximumBufferIndex());
		if(m_internalBufferList.size() > MAXIMUM_SIZE) {
			m_internalBufferList.pop_front();
			m_numberOfFirstBuffer++;
		}
	}

	const Buffer & returnBuffer(const unsigned long int bufferPosition) {
		if(bufferPosition >= m_numberOfFirstBuffer and bufferPosition <= getMaximumBufferIndex()) {
			unsigned int index = bufferPosition - m_numberOfFirstBuffer;
			return m_internalBufferList[index];
		}
		else
			throw indexException;
	}

	unsigned long int getNumberOfFirstBuffer() const {
		return m_numberOfFirstBuffer;
	}

	unsigned long int getMaximumBufferIndex() const {
		if(m_internalBufferList.size() > 0)
			return m_numberOfFirstBuffer + m_internalBufferList.size() - 1;
		else
			return -1;
	}

	unsigned long int getNumberOfBufferForClient(Socket & listener) {
		unsigned long int bufferIndex = listener.getBufferIndex();
		if(bufferIndex < m_numberOfFirstBuffer) {
			listener.setBufferIndex(m_numberOfFirstBuffer + 1);
			return m_numberOfFirstBuffer;
		}
		else if(bufferIndex <= getMaximumBufferIndex()) {
			listener.setBufferIndex(bufferIndex + 1);
			return bufferIndex;
		}
		else
			return -1;
	}

private:
	const unsigned int MAXIMUM_SIZE = 10;
	long unsigned int m_numberOfFirstBuffer;
	std::deque<Buffer> m_internalBufferList;
};
