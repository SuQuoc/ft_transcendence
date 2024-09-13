// I see a high lvl langue where you need 40 lines for a simple task
// just checks if the socket is open

const waitForOpenConnection = (socket) => {
    return new Promise((resolve, reject) => {
        const maxNumberOfAttempts = 10
        const intervalTime = 200 //ms

        let currentAttempt = 0
        const interval = setInterval(() => {
            if (currentAttempt > maxNumberOfAttempts - 1) {
                clearInterval(interval)
                reject(new Error('Maximum number of attempts exceeded'))
            } else if (socket.readyState === socket.OPEN) {
                clearInterval(interval)
                resolve()
            }
            currentAttempt++
        }, intervalTime)
    })
}

function send_room_size(chatSocket, room_size) {
    chatSocket.send(
        JSON.stringify({
            type: 'roomSize',
            roomSize: room_size,
        })
    )
}

const sendRoomSizeMessage = async (socket, room_size) => {
    if (socket.readyState !== socket.OPEN) {
        try {
            await waitForOpenConnection(socket)
            send_room_size(socket, room_size)
        } catch (err) {
            console.error(err)
        }
    } else {
        socket.send(msg)
    }
}
