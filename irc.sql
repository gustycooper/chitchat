DROP DATABASE IF EXISTS chat;
CREATE DATABASE chat;
\c chat;
CREATE EXTENSION pgcrypto;
--
-- Table structure for table messages
--
DROP TABLE IF EXISTS messages;
CREATE TABLE IF NOT EXISTS messages (
  id serial NOT NULL,
  userid varchar(70) NOT NULL,
  message varchar(200) NOT NULL,
  PRIMARY KEY (id)
) ;

INSERT INTO messages (userid, message) VALUES
('TheWolfman', 'Watchout for the Wolfman'),
('Gusty', 'Gusty programmed some of this code');

--
-- Table structure for table users
--

DROP TABLE IF EXISTS users;
CREATE TABLE IF NOT EXISTS users (
  id serial NOT NULL,
  username varchar(12) NOT NULL,
  password varchar(126) NOT NULL,
  restrictions varchar(126) NOT NULL,
  PRIMARY KEY (id)
)  ;

---  INSERT INTO users (username,password,restrictions) VALUES ('raz',crypt('p00d13',gen_salt('bf')),'none')
INSERT INTO users (username, password, restrictions) VALUES
('raz', crypt('p00d13',gen_salt('bf')), 'none'),
('ann', crypt('changeme',gen_salt('bf')), 'none'),
('gusty', crypt('gusty',gen_salt('bf')), 'none'),
('jerrianne', crypt('jerrianne',gen_salt('bf')), 'none'),
('jeremy', crypt('jeremy',gen_salt('bf')), 'none'),
('brandalee', crypt('brandalee',gen_salt('bf')), 'none'),
('zachary', crypt('zachary',gen_salt('bf')), 'none'),
('emily', crypt('emily',gen_salt('bf')), 'none'),
('lee', crypt('lee',gen_salt('bf')), 'none'),
('lazy', crypt('qwerty',gen_salt('bf')), 'none');



