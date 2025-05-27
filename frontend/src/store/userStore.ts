// userStore.js
import api from '../lib/api'

let username: string = ''

const loadUsername = async (accessToken: string | null) => {
	try {
		const res = await api.get('/user', {
			headers: {
				Authorization: `Bearer ${accessToken}`
			}
		})
		username = res.data
		console.log('Username loaded:', username)
		
		loadPublicKey(username, accessToken)
	} catch (err) {
		console.error('Error loading username:', err)
	}
}

const getUsername = () => username

let public_key: string = ''

const loadPublicKey = async (username: string, accessToken: string | null) => {
	try {
		const res = await api.get(`/users/${username}/key`, {
			headers: {
				Authorization: `Bearer ${accessToken}`
			}
		})
		username = res.data
		console.log('Public Key loaded:', username)
	} catch (err) {
		console.error('Error loading Public Key:', err)
	}
}

const getPublicKey = () => public_key

export { loadUsername, getUsername, loadPublicKey, getPublicKey }