/*
 * SocketList_test.cpp
 *
 *  Created on: 02.01.2015
 *      Author: nils
 */

#include "../SocketList.h"
#include <gtest/gtest.h>


class SocketListTest : public ::testing::Test {
public:
	void SetUp() {
		m_testServer = socket(PF_INET, SOCK_STREAM, 0);

		struct sockaddr_in serverAddress;
		serverAddress.sin_addr.s_addr = INADDR_ANY;
		serverAddress.sin_port = 0;
		serverAddress.sin_family = AF_INET;

		ASSERT_NE(bind(m_testServer, reinterpret_cast<struct sockaddr*>(&serverAddress), sizeof(serverAddress)),
				-1);

		socklen_t dummyLength = sizeof(serverAddress);
		getsockname(m_testServer, reinterpret_cast<struct sockaddr*>(&serverAddress), &dummyLength);

		ASSERT_NE(listen(m_testServer, 3), -1);

		m_testClient = socket(PF_INET, SOCK_STREAM, 0);
		ASSERT_NE(connect(m_testClient, reinterpret_cast<struct sockaddr*>(&serverAddress), sizeof(serverAddress)), -1);

		m_testClient2 = socket(PF_INET, SOCK_STREAM, 0);
		ASSERT_NE(connect(m_testClient2, reinterpret_cast<struct sockaddr*>(&serverAddress), sizeof(serverAddress)), -1);
	}

	void TearDown() {
		close(m_testServer);
		close(m_testClient);
		close(m_testClient2);
	}

	int m_testServer;
	int m_testClient, m_testClient2;

	SocketList m_testSocketList;

};

TEST_F(SocketListTest, Accept) {
	m_testSocketList.acceptFromServer(m_testServer);

	EXPECT_EQ(m_testSocketList.size(), 1);

	m_testSocketList.acceptFromServer(m_testServer);

	ASSERT_EQ(m_testSocketList.size(), 2);

	std::vector<Socket>::iterator firstElement = m_testSocketList.begin();
	std::vector<Socket>::iterator secondElement = m_testSocketList.begin();
	secondElement++;

	EXPECT_NE(firstElement->getSocketIPPort(), secondElement->getSocketIPPort());
	EXPECT_NE(firstElement->getInternalFileDescriptor(), secondElement->getInternalFileDescriptor());
	EXPECT_EQ(firstElement->getSocketIPAddress().s_addr, secondElement->getSocketIPAddress().s_addr);
}

TEST_F(SocketListTest, Remove) {
	m_testSocketList.acceptFromServer(m_testServer);
	m_testSocketList.acceptFromServer(m_testServer);

	ASSERT_EQ(m_testSocketList.size(), 2);

	std::vector<Socket>::iterator firstElement = m_testSocketList.begin();
	std::vector<Socket>::iterator secondElement = m_testSocketList.begin();
	secondElement++;

	m_testSocketList.removeSocket(firstElement->getInternalFileDescriptor());

	ASSERT_EQ(m_testSocketList.size(), 1);

	EXPECT_THROW(m_testSocketList.removeSocket(firstElement->getInternalFileDescriptor() + firstElement->getInternalFileDescriptor()), SocketLookupException);
}
