const facebook = require("facebook-chat-api");
const fs = require('fs');

function fetchThreadInfo(
  api,
  threadId
) {
  return new Promise((resolve, reject) => {
    return api.getThreadInfo(threadId, (err, data) => {
      if (err) return reject(Error(err.error));

      return resolve(data);
    });
  });
}

function fetchThreadHistory(
  api,
  threadId
) {
  return new Promise((resolve, reject) => {
    return api.getThreadHistory(threadId, 2000, undefined, (err, data) => {
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


async function main() {
  const session = await getApi({ email: "USER_EMAIL", password: "USER_PASSWORD" }, {});
  const threadInfo = await fetchThreadInfo(session, 'THREAD_ID');
  const members = await fetchMembers(session, threadInfo.participantIDs);
  const messages = await fetchThreadHistory(session, 'THREAD_ID');
  fs.writeFileSync('./data.json', JSON.stringify({members, messages}));
}

main()
