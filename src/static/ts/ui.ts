/**
 * JSON response after sending add channel request to server.
 */
interface addChannelJSON {
    success: boolean
    errorMessage?: string
}

/**
 * Get server response from add channel request to server.
 * @param channelName  name of the channel to be added.
 * @return Promise with JSON of the response.
 */
function getResponseAddChannel(channelName: string): Promise<addChannelJSON> {
    return new Promise((resolve) => {
        const xhr: XMLHttpRequest = new XMLHttpRequest()
        xhr.open('POST', '/add-channel')

        xhr.responseType = 'json'

        xhr.onload = () => {
            resolve(xhr.response)
        }

        const form: FormData = new FormData()
        form.append('channelName', channelName)

        xhr.send(form)
    })
}

/**
 * Close the modal after adding a channel.
 */
function closeModal(): void {
    const closeButton: HTMLButtonElement = document.querySelector('#add-channel-close-button')
    closeButton.click()
}

/**
 * Show an alert after sending an invalid channel name.
 * @param error  error message.
 */
function invalidChannelName(error: string): void {
    alert(`Invalid channel name, error message: ${error}.`)
}

/**
 * Show an alert after successfully adding a channel.
 */
function addChannelMessage() {
    alert('The channel was successfully added!')
}

/**
 * Manage the add channel modal. If input field has a valid channel name, create a channel.
 * Otherwise, show a corresponding error.
 */
function addChannelModal(): void {

    const input: HTMLButtonElement = document.querySelector('#add-channel-input')
    const addButton: HTMLButtonElement = document.querySelector('#add-channel-add-button')

    addButton.addEventListener('click', async () => {
        const channelName: string = input.value
        const responseAddChannel: addChannelJSON = await getResponseAddChannel(channelName)
        if (responseAddChannel.success) {
            addChannelMessage()
            closeModal()
        } else {
            invalidChannelName(responseAddChannel.errorMessage)
        }
    })
}

let channel = undefined

interface singleMessageJSON {
    user: string
    content: string
    time: string
}

interface messagesJSON {
    messages: singleMessageJSON[]
}

function getResponseMessages(channelName: string): Promise<messagesJSON> {
    return new Promise<messagesJSON>(resolve => {
        const xhr: XMLHttpRequest = new XMLHttpRequest()
        xhr.open('POST', '/get-messages')
        xhr.responseType = 'json'
        xhr.onload = () => {
            resolve(xhr.response)
        }
        const data: FormData = new FormData()
        data.append('channelName', channelName)
        xhr.send(data)
    })
}

function switchChannel(channel: HTMLElement) {
    channel.addEventListener('click', async function () {
        const hideSwitchChannel: HTMLDivElement = document.querySelector('#hide-switch-channel')
        hideSwitchChannel.style.display = 'block'

        const channel = this.dataset.channel
        const channelNameInfo: HTMLElement = document.querySelector('#channel-info h3')
        channelNameInfo.innerHTML = channel

        const responseMessages: messagesJSON = await getResponseMessages(channel)
        console.log(responseMessages)
        const messages: singleMessageJSON[] = responseMessages.messages
        const messagesDiv: HTMLDivElement = document.querySelector('#messages-list')
        messagesDiv.innerHTML = ''
        messages.forEach(message => {
            console.log(message)
            const ul = document.createElement('ul')
            ul.innerHTML = `<b>${message.user}</b> - ${message.time} : ${message.content}`
            messagesDiv.append(ul)
        })
    })
}

function channelSwitcher(): void {
    document.querySelectorAll('.channel').forEach(
        channel => switchChannel(<HTMLElement>channel)
    )
}

document.addEventListener('DOMContentLoaded', () => {
    addChannelModal()
    channelSwitcher()
})