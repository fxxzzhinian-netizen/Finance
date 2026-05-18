import request from './request'

export function aiParseSearch(text, target = 'assets') {
  return request.post('/api/ai/parse-search', { text, target }, {
    timeout: 20000,
  })
}
