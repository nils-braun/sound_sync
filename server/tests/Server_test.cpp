/*
 * Server_test.cpp
 *
 *  Created on: 02.01.2015
 *      Author: nils
 */

#include "../Server.h"
#include "../Socket.h"
#include <gtest/gtest.h>
#include <sys/socket.h>


class ServerTest : public ::testing::Test {
public:
	void SetUp() {
	}

	void TearDown() {
	}

	Server m_testServer;
};

TEST_F(ServerTest, Listening) {

	m_testServer.startListeningSteppwise();

	int int_testClient = socket(PF_INET, SOCK_STREAM, 0);
	struct sockaddr_in serverAddress;
	serverAddress.sin_addr.s_addr = INADDR_ANY;
	serverAddress.sin_port = htons(50007);
	serverAddress.sin_family = AF_INET;
	ASSERT_NE(connect(int_testClient, reinterpret_cast<struct sockaddr*>(&serverAddress), sizeof(serverAddress)), -1);

	Socket testClient;
	ASSERT_NO_THROW(m_testServer.mainLoop());
	close(int_testClient);

	EXPECT_EQ(m_testServer.size(), 1);

}

TEST_F(ServerTest, ListeningMany) {

	m_testServer.startListeningSteppwise();

	int int_testClient[10];
	struct sockaddr_in serverAddress;
	serverAddress.sin_addr.s_addr = INADDR_ANY;
	serverAddress.sin_port = htons(50007);
	serverAddress.sin_family = AF_INET;

	for(int i = 0; i < 5; ++i) {
		int_testClient[i] = socket(PF_INET, SOCK_STREAM, 0);
		ASSERT_NE(connect(int_testClient[i], reinterpret_cast<struct sockaddr*>(&serverAddress), sizeof(serverAddress)), -1);
	}

	Socket testClient;
	for(int i = 0; i < 5; ++i) {
		ASSERT_NO_THROW(m_testServer.mainLoop());
	}


	EXPECT_EQ(m_testServer.size(), 5);
}
