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
	} catch (err) {
		console.error('Error loading username:', err)
	}
}

const getUsername = () => username

export { loadUsername, getUsername }