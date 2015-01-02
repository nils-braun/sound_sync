/*
 * Socket_test.cpp
 *
 *  Created on: 31.12.2014
 *      Author: nils
 */

#include "../Socket.h"

#include <sys/socket.h>
#include <gtest/gtest.h>
#include <unistd.h>

class SocketTest : public ::testing::Test {
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

		m_testSocket.acceptFromServer(m_testServer);
	}

	void TearDown() {
		close(m_testClient);
		close(m_testServer);
	}

	int m_testServer;
	int m_testClient;

	Socket m_testSocket;
};

TEST_F(SocketTest, AcceptFromServer) {
	struct sockaddr_in serverAddress;
	serverAddress.sin_addr.s_addr = INADDR_LOOPBACK;
	serverAddress.sin_port = 0;
	serverAddress.sin_family = AF_INET;

	socklen_t dummyLength = sizeof(serverAddress);
	getsockname(m_testClient, reinterpret_cast<struct sockaddr*>(&serverAddress), &dummyLength);

	EXPECT_EQ(m_testSocket.getSocketIPAddress().s_addr, serverAddress.sin_addr.s_addr);
	EXPECT_EQ(m_testSocket.getSocketIPPort(), serverAddress.sin_port);
	EXPECT_EQ(m_testSocket.getSocketType(), Socket::SocketType::UndefinedClientType);
}

TEST_F(SocketTest, SocketType) {
	m_testSocket.setSocketType(Socket::SocketType::ListenerType);

	EXPECT_EQ(m_testSocket.getSocketType(), Socket::SocketType::ListenerType);
}

