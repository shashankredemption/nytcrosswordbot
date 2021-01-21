const facebook = require("facebook-chat-api");
const fs = require('fs');

function fetchThreadInfo(
  api,
  threadId
) {
  return new Promise((resolve, reject) => {
    return api.getThreadInfo(threadId, (err, data) => {
      if (err) {
        console.log(err.error);
        return reject(Error(err.error));
      }

      return resolve(data);
    });
  });
}

function fetchThreadHistory(
  api,
  threadId
) {
  return new Promise((resolve, reject) => {
    return api.getThreadHistory(threadId, 200, undefined, (err, data) => {
      if (err) return reject(Error(err.error));

      return resolve(data);
    });
  });
}

function fetchMembers(
  api,
  participantIds
) {
  return new Promise((resolve, reject) => {
    return api.getUserInfo(participantIds, (err, data) => {
      if (err) return reject(Error(err.error));

      return resolve(data);
    });
  });
}

function getApi(
  payload,
  config
) {
  return new Promise((resolve, reject) => {
    return facebook(payload, config, (err, api) => {
      if (err) {
        return reject(Error(`Failed to login: ${err.error}`));
      }

      console.log('Successfully logged in');

      if (!api) {
        return reject(Error('api failed to load'));
      }
      return resolve(api);
    });
  });
}

function sleep(milliseconds) {
  const date = Date.now();
  let currentDate = null;
  do {
    currentDate = Date.now();
  } while (currentDate - date < milliseconds);
}

async function main() {
  const cookie_chrome = require('./cookie.json');
  const cookie = [];

  for (let cch of cookie_chrome) {
    let c = Object.assign({}, cch);

        // convert to appState key/value
    c.key = c.name;
    c.domain = c.domain.replace(/^\./,'');

    cookie.push(c);
  }

  fs.writeFileSync('appstate.json', JSON.stringify(cookie));
  const session = await getApi({appState: JSON.parse(fs.readFileSync('appstate.json', 'utf8'))}, {});
  sleep(1000);
  const threadInfo = await fetchThreadInfo(session, 'THREAD_ID');
  sleep(1000);
  const members = await fetchMembers(session, threadInfo.participantIDs);
  sleep(1000);
  const messages = await fetchThreadHistory(session, 'THREAD_ID');
  sleep(1000);
  fs.writeFileSync('./data.json', JSON.stringify({members, messages}));
}

main()
