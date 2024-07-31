-- phpMyAdmin SQL Dump
-- version 5.1.1deb5ubuntu1
-- https://www.phpmyadmin.net/
--
-- Servidor: localhost:3306
-- Tiempo de generación: 29-07-2024 a las 11:29:36
-- Versión del servidor: 8.0.35-0ubuntu0.22.04.1
-- Versión de PHP: 8.1.2-1ubuntu2.14

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `twitter_negra`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `annotation`
--

CREATE TABLE `annotation` (
  `id` int NOT NULL,
  `type` varchar(200) DEFAULT NULL,
  `probability` double DEFAULT NULL,
  `normalized_text` varchar(400) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `annotation_prediction_tweet`
--

CREATE TABLE `annotation_prediction_tweet` (
  `id` int NOT NULL,
  `tweet_id` int NOT NULL,
  `annotation_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `annotation_tweet`
--

CREATE TABLE `annotation_tweet` (
  `id` int NOT NULL,
  `tweet_id` int NOT NULL,
  `domain_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `detox_latam`
--

CREATE TABLE `detox_latam` (
  `id` int NOT NULL,
  `rusia` tinyint(1) DEFAULT NULL,
  `china` tinyint(1) DEFAULT NULL,
  `iran` tinyint(1) DEFAULT NULL,
  `cuba` tinyint(1) DEFAULT NULL,
  `venezuela` tinyint(1) DEFAULT NULL,
  `nicaragua` tinyint(1) DEFAULT NULL,
  `spain_criticism` tinyint(1) DEFAULT NULL,
  `user_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `domain`
--

CREATE TABLE `domain` (
  `id` int NOT NULL,
  `annotation_id` varchar(400) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `name` varchar(250) DEFAULT NULL,
  `description` text,
  `category` varchar(250) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `hashtag`
--

CREATE TABLE `hashtag` (
  `id` int NOT NULL,
  `hashtag` varchar(250) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `hashtagt_tweet`
--

CREATE TABLE `hashtagt_tweet` (
  `id` int NOT NULL,
  `hashtag_id` int NOT NULL,
  `tweet_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `hate_speech`
--

CREATE TABLE `hate_speech` (
  `id` int NOT NULL,
  `tweet_id` int NOT NULL,
  `hate` double NOT NULL,
  `non_hate` double NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `liwc_2007`
--

CREATE TABLE `liwc_2007` (
  `id` int NOT NULL,
  `Funct` int DEFAULT NULL,
  `TotPron` int DEFAULT NULL,
  `Yo` int DEFAULT NULL,
  `PronPer` int DEFAULT NULL,
  `Nosotro` int DEFAULT NULL,
  `TuUtd` int DEFAULT NULL,
  `ElElla` int DEFAULT NULL,
  `Ellos` int DEFAULT NULL,
  `PronImp` int DEFAULT NULL,
  `Articulo` int DEFAULT NULL,
  `Verbos` int DEFAULT NULL,
  `VerbAux` int DEFAULT NULL,
  `Pasado` int DEFAULT NULL,
  `Present` int DEFAULT NULL,
  `Futuro` int DEFAULT NULL,
  `Adverb` int DEFAULT NULL,
  `Prepos` int DEFAULT NULL,
  `Conjunc` int DEFAULT NULL,
  `Negacio` int DEFAULT NULL,
  `Cuantif` int DEFAULT NULL,
  `Numeros` int DEFAULT NULL,
  `Maldec` int DEFAULT NULL,
  `verbYO` int DEFAULT NULL,
  `verbTU` int DEFAULT NULL,
  `verbNOS` int DEFAULT NULL,
  `verbosEL` int DEFAULT NULL,
  `verbELLOS` int DEFAULT NULL,
  `Subjuntiv` int DEFAULT NULL,
  `VosUtds` int DEFAULT NULL,
  `formal` int DEFAULT NULL,
  `informal` int DEFAULT NULL,
  `verbVos` int DEFAULT NULL,
  `Social` int DEFAULT NULL,
  `Familia` int DEFAULT NULL,
  `Amigos` int DEFAULT NULL,
  `Humanos` int DEFAULT NULL,
  `Afect` int DEFAULT NULL,
  `EmoPos` int DEFAULT NULL,
  `EmoNeg` int DEFAULT NULL,
  `Ansiedad` int DEFAULT NULL,
  `Enfado` int DEFAULT NULL,
  `Triste` int DEFAULT NULL,
  `MecCog` int DEFAULT NULL,
  `Insight` int DEFAULT NULL,
  `Causa` int DEFAULT NULL,
  `Discrep` int DEFAULT NULL,
  `Tentat` int DEFAULT NULL,
  `Certeza` int DEFAULT NULL,
  `Inhib` int DEFAULT NULL,
  `Incl` int DEFAULT NULL,
  `Excl` int DEFAULT NULL,
  `Percept` int DEFAULT NULL,
  `Ver` int DEFAULT NULL,
  `Oir` int DEFAULT NULL,
  `Sentir` int DEFAULT NULL,
  `Biolog` int DEFAULT NULL,
  `Cuerpo` int DEFAULT NULL,
  `Salud` int DEFAULT NULL,
  `Sexual` int DEFAULT NULL,
  `Ingerir` int DEFAULT NULL,
  `Relativ` int DEFAULT NULL,
  `Movim` int DEFAULT NULL,
  `Espacio` int DEFAULT NULL,
  `Tiempo` int DEFAULT NULL,
  `Trabajo` int DEFAULT NULL,
  `Logro` int DEFAULT NULL,
  `Placer` int DEFAULT NULL,
  `Hogar` int DEFAULT NULL,
  `Dinero` int DEFAULT NULL,
  `Relig` int DEFAULT NULL,
  `Muerte` int DEFAULT NULL,
  `Asentir` int DEFAULT NULL,
  `NoFluen` int DEFAULT NULL,
  `Relleno` int DEFAULT NULL,
  `tweet_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `liwc_2015`
--

CREATE TABLE `liwc_2015` (
  `id` int NOT NULL,
  `tweet_id` int NOT NULL,
  `pronoun` int DEFAULT NULL,
  `ppron` int DEFAULT NULL,
  `i` int DEFAULT NULL,
  `we` int DEFAULT NULL,
  `you` int DEFAULT NULL,
  `shehe` int DEFAULT NULL,
  `they` int DEFAULT NULL,
  `ipron` int DEFAULT NULL,
  `article` int DEFAULT NULL,
  `prep` int DEFAULT NULL,
  `auxverb` int DEFAULT NULL,
  `adverb` int DEFAULT NULL,
  `conj` int DEFAULT NULL,
  `negate` int DEFAULT NULL,
  `othergram` int DEFAULT NULL,
  `verb` int DEFAULT NULL,
  `adj` int DEFAULT NULL,
  `compare` int DEFAULT NULL,
  `interrog` int DEFAULT NULL,
  `number` int DEFAULT NULL,
  `quant` int DEFAULT NULL,
  `affect` int DEFAULT NULL,
  `posemo` int DEFAULT NULL,
  `negemo` int DEFAULT NULL,
  `anx` int DEFAULT NULL,
  `anger` int DEFAULT NULL,
  `sad` int DEFAULT NULL,
  `social` int DEFAULT NULL,
  `family` int DEFAULT NULL,
  `friend` int DEFAULT NULL,
  `female` int DEFAULT NULL,
  `male` int DEFAULT NULL,
  `cogproc` int DEFAULT NULL,
  `insight` int DEFAULT NULL,
  `cause` int DEFAULT NULL,
  `discrep` int DEFAULT NULL,
  `tentat` int DEFAULT NULL,
  `certain` int DEFAULT NULL,
  `differ` int DEFAULT NULL,
  `percept` int DEFAULT NULL,
  `see` int DEFAULT NULL,
  `hear` int DEFAULT NULL,
  `feel` int DEFAULT NULL,
  `bio` int DEFAULT NULL,
  `body` int DEFAULT NULL,
  `health` int DEFAULT NULL,
  `sexual` int DEFAULT NULL,
  `ingest` int DEFAULT NULL,
  `drives` int DEFAULT NULL,
  `affiliation` int DEFAULT NULL,
  `achieve` int DEFAULT NULL,
  `power` int DEFAULT NULL,
  `reward` int DEFAULT NULL,
  `risk` int DEFAULT NULL,
  `timeorient` int DEFAULT NULL,
  `focuspast` int DEFAULT NULL,
  `focuspresent` int DEFAULT NULL,
  `focusfuture` int DEFAULT NULL,
  `relativ` int DEFAULT NULL,
  `motion` int DEFAULT NULL,
  `space` int DEFAULT NULL,
  `time` int DEFAULT NULL,
  `persconc` int DEFAULT NULL,
  `work` int DEFAULT NULL,
  `leisure` int DEFAULT NULL,
  `home` int DEFAULT NULL,
  `money` int DEFAULT NULL,
  `relig` int DEFAULT NULL,
  `death` int DEFAULT NULL,
  `informal` int DEFAULT NULL,
  `swear` int DEFAULT NULL,
  `netspeak` int DEFAULT NULL,
  `assent` int DEFAULT NULL,
  `nonflu` int DEFAULT NULL,
  `filler` int DEFAULT NULL,
  `funct` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `mention`
--

CREATE TABLE `mention` (
  `id` int NOT NULL,
  `tweet_id` int NOT NULL,
  `user_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `quoted`
--

CREATE TABLE `quoted` (
  `id` int NOT NULL,
  `tweet_id` int NOT NULL,
  `quoted` varchar(400) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `reply`
--

CREATE TABLE `reply` (
  `id` int NOT NULL,
  `tweet_id` int NOT NULL,
  `reply_to` varchar(400) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `retweet`
--

CREATE TABLE `retweet` (
  `id` int NOT NULL,
  `tweet_id` int NOT NULL,
  `retweeted` varchar(250) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `sentiment`
--

CREATE TABLE `sentiment` (
  `id` int NOT NULL,
  `tweet_id` int NOT NULL,
  `positive` double NOT NULL,
  `negative` double NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tweet`
--

CREATE TABLE `tweet` (
  `id` int NOT NULL,
  `tweet_id` varchar(200) NOT NULL,
  `source` varchar(200) DEFAULT NULL,
  `reply_settings` varchar(200) DEFAULT NULL,
  `possibly_sensitive` tinyint(1) DEFAULT NULL,
  `author_id` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `lang` varchar(4) DEFAULT NULL,
  `conversation_id` varchar(200) DEFAULT NULL,
  `text` varchar(800) NOT NULL,
  `start_time` datetime DEFAULT NULL,
  `end_time` datetime DEFAULT NULL,
  `trending_topic` varchar(200) NOT NULL,
  `campaign` varchar(200) NOT NULL,
  `in_reply_to_user_id` varchar(250) DEFAULT NULL,
  `mentions_psoe` tinyint(1) DEFAULT NULL,
  `mentions_pp` tinyint(1) DEFAULT NULL,
  `mentions_vox` tinyint(1) DEFAULT NULL,
  `mentions_liberal` tinyint(1) DEFAULT NULL,
  `mentions_conservative` tinyint(1) DEFAULT NULL,
  `mentions_podemos` tinyint(1) DEFAULT NULL,
  `mentions_communism` tinyint(1) DEFAULT NULL,
  `mentions_gender` tinyint(1) DEFAULT NULL,
  `mentions_cs` tinyint(1) DEFAULT NULL,
  `mentions_independentism` tinyint(1) DEFAULT NULL,
  `mentions_spain` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tweet_metrics`
--

CREATE TABLE `tweet_metrics` (
  `id` int NOT NULL,
  `tweet_id` int NOT NULL,
  `date` datetime DEFAULT CURRENT_TIMESTAMP,
  `retweet_count` int NOT NULL,
  `reply_count` int NOT NULL,
  `like_count` int NOT NULL,
  `quote_count` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `url`
--

CREATE TABLE `url` (
  `id` int NOT NULL,
  `url` varchar(400) NOT NULL,
  `expanded_url` text,
  `domain` varchar(300) DEFAULT NULL,
  `title` text,
  `description` text,
  `unwound_url` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `url_tweet`
--

CREATE TABLE `url_tweet` (
  `id` int NOT NULL,
  `tweet_id` int NOT NULL,
  `url_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `user`
--

CREATE TABLE `user` (
  `id` int NOT NULL,
  `username` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `user_id` varchar(200) NOT NULL,
  `description` text,
  `creation_date` datetime DEFAULT NULL,
  `followers_num` int DEFAULT NULL,
  `following_num` int DEFAULT NULL,
  `url` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `location` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `annotation`
--
ALTER TABLE `annotation`
  ADD PRIMARY KEY (`id`),
  ADD KEY `type` (`type`),
  ADD KEY `normalized_text` (`normalized_text`);

--
-- Indices de la tabla `annotation_prediction_tweet`
--
ALTER TABLE `annotation_prediction_tweet`
  ADD PRIMARY KEY (`id`),
  ADD KEY `tweet_id` (`tweet_id`),
  ADD KEY `annotation_id` (`annotation_id`);

--
-- Indices de la tabla `annotation_tweet`
--
ALTER TABLE `annotation_tweet`
  ADD PRIMARY KEY (`id`),
  ADD KEY `tweet_id` (`tweet_id`),
  ADD KEY `domain_id` (`domain_id`);

--
-- Indices de la tabla `detox_latam`
--
ALTER TABLE `detox_latam`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indices de la tabla `domain`
--
ALTER TABLE `domain`
  ADD PRIMARY KEY (`id`),
  ADD KEY `category` (`category`),
  ADD KEY `name` (`name`);

--
-- Indices de la tabla `hashtag`
--
ALTER TABLE `hashtag`
  ADD PRIMARY KEY (`id`),
  ADD KEY `hashtag` (`hashtag`);

--
-- Indices de la tabla `hashtagt_tweet`
--
ALTER TABLE `hashtagt_tweet`
  ADD PRIMARY KEY (`id`),
  ADD KEY `tweet_id` (`tweet_id`),
  ADD KEY `hashtagt_tweet_ibfk_2` (`hashtag_id`);

--
-- Indices de la tabla `hate_speech`
--
ALTER TABLE `hate_speech`
  ADD PRIMARY KEY (`id`),
  ADD KEY `tweet_id` (`tweet_id`);

--
-- Indices de la tabla `liwc_2007`
--
ALTER TABLE `liwc_2007`
  ADD PRIMARY KEY (`id`),
  ADD KEY `tweet_id` (`tweet_id`);

--
-- Indices de la tabla `liwc_2015`
--
ALTER TABLE `liwc_2015`
  ADD PRIMARY KEY (`id`),
  ADD KEY `tweet_id` (`tweet_id`);

--
-- Indices de la tabla `mention`
--
ALTER TABLE `mention`
  ADD PRIMARY KEY (`id`),
  ADD KEY `tweet_id` (`tweet_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indices de la tabla `quoted`
--
ALTER TABLE `quoted`
  ADD PRIMARY KEY (`id`),
  ADD KEY `tweet_id` (`tweet_id`),
  ADD KEY `quoted` (`quoted`);

--
-- Indices de la tabla `reply`
--
ALTER TABLE `reply`
  ADD PRIMARY KEY (`id`),
  ADD KEY `tweet_id` (`tweet_id`),
  ADD KEY `reply_to` (`reply_to`);

--
-- Indices de la tabla `retweet`
--
ALTER TABLE `retweet`
  ADD PRIMARY KEY (`id`),
  ADD KEY `retweeted` (`retweeted`),
  ADD KEY `tweet_id` (`tweet_id`);

--
-- Indices de la tabla `sentiment`
--
ALTER TABLE `sentiment`
  ADD PRIMARY KEY (`id`),
  ADD KEY `tweet_id` (`tweet_id`);

--
-- Indices de la tabla `tweet`
--
ALTER TABLE `tweet`
  ADD PRIMARY KEY (`id`),
  ADD KEY `campaign` (`campaign`),
  ADD KEY `trending_topic` (`trending_topic`),
  ADD KEY `conversation_id` (`conversation_id`),
  ADD KEY `tweet_id` (`tweet_id`),
  ADD KEY `author_id` (`author_id`),
  ADD KEY `in_reply_to_user_id` (`in_reply_to_user_id`);

--
-- Indices de la tabla `tweet_metrics`
--
ALTER TABLE `tweet_metrics`
  ADD PRIMARY KEY (`id`),
  ADD KEY `tweet_id` (`tweet_id`);

--
-- Indices de la tabla `url`
--
ALTER TABLE `url`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `url_tweet`
--
ALTER TABLE `url_tweet`
  ADD PRIMARY KEY (`id`),
  ADD KEY `tweet_id` (`tweet_id`),
  ADD KEY `url_id` (`url_id`);

--
-- Indices de la tabla `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `annotation`
--
ALTER TABLE `annotation`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `annotation_prediction_tweet`
--
ALTER TABLE `annotation_prediction_tweet`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `annotation_tweet`
--
ALTER TABLE `annotation_tweet`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `detox_latam`
--
ALTER TABLE `detox_latam`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `domain`
--
ALTER TABLE `domain`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `hashtag`
--
ALTER TABLE `hashtag`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `hashtagt_tweet`
--
ALTER TABLE `hashtagt_tweet`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `hate_speech`
--
ALTER TABLE `hate_speech`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `liwc_2007`
--
ALTER TABLE `liwc_2007`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `liwc_2015`
--
ALTER TABLE `liwc_2015`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `mention`
--
ALTER TABLE `mention`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `quoted`
--
ALTER TABLE `quoted`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `reply`
--
ALTER TABLE `reply`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `retweet`
--
ALTER TABLE `retweet`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `sentiment`
--
ALTER TABLE `sentiment`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `tweet`
--
ALTER TABLE `tweet`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `tweet_metrics`
--
ALTER TABLE `tweet_metrics`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `url`
--
ALTER TABLE `url`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `url_tweet`
--
ALTER TABLE `url_tweet`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `user`
--
ALTER TABLE `user`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `annotation_prediction_tweet`
--
ALTER TABLE `annotation_prediction_tweet`
  ADD CONSTRAINT `annotation_prediction_tweet_ibfk_1` FOREIGN KEY (`tweet_id`) REFERENCES `tweet` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `annotation_prediction_tweet_ibfk_2` FOREIGN KEY (`annotation_id`) REFERENCES `annotation` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `annotation_tweet`
--
ALTER TABLE `annotation_tweet`
  ADD CONSTRAINT `annotation_tweet_ibfk_1` FOREIGN KEY (`tweet_id`) REFERENCES `tweet` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `annotation_tweet_ibfk_2` FOREIGN KEY (`domain_id`) REFERENCES `domain` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `detox_latam`
--
ALTER TABLE `detox_latam`
  ADD CONSTRAINT `detox_latam_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `hashtagt_tweet`
--
ALTER TABLE `hashtagt_tweet`
  ADD CONSTRAINT `hashtagt_tweet_ibfk_1` FOREIGN KEY (`tweet_id`) REFERENCES `tweet` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `hashtagt_tweet_ibfk_2` FOREIGN KEY (`hashtag_id`) REFERENCES `hashtag` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `hate_speech`
--
ALTER TABLE `hate_speech`
  ADD CONSTRAINT `hate_speech_ibfk_1` FOREIGN KEY (`tweet_id`) REFERENCES `tweet` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `liwc_2007`
--
ALTER TABLE `liwc_2007`
  ADD CONSTRAINT `liwc_2007_ibfk_1` FOREIGN KEY (`tweet_id`) REFERENCES `tweet` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `liwc_2015`
--
ALTER TABLE `liwc_2015`
  ADD CONSTRAINT `liwc_2015_ibfk_1` FOREIGN KEY (`tweet_id`) REFERENCES `tweet` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `mention`
--
ALTER TABLE `mention`
  ADD CONSTRAINT `mention_ibfk_1` FOREIGN KEY (`tweet_id`) REFERENCES `tweet` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `mention_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `quoted`
--
ALTER TABLE `quoted`
  ADD CONSTRAINT `quoted_ibfk_1` FOREIGN KEY (`tweet_id`) REFERENCES `tweet` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `reply`
--
ALTER TABLE `reply`
  ADD CONSTRAINT `reply_ibfk_1` FOREIGN KEY (`tweet_id`) REFERENCES `tweet` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `retweet`
--
ALTER TABLE `retweet`
  ADD CONSTRAINT `retweet_ibfk_1` FOREIGN KEY (`tweet_id`) REFERENCES `tweet` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `sentiment`
--
ALTER TABLE `sentiment`
  ADD CONSTRAINT `sentiment_ibfk_1` FOREIGN KEY (`tweet_id`) REFERENCES `tweet` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `tweet`
--
ALTER TABLE `tweet`
  ADD CONSTRAINT `tweet_ibfk_1` FOREIGN KEY (`author_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `tweet_metrics`
--
ALTER TABLE `tweet_metrics`
  ADD CONSTRAINT `tweet_metrics_ibfk_1` FOREIGN KEY (`tweet_id`) REFERENCES `tweet` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `url_tweet`
--
ALTER TABLE `url_tweet`
  ADD CONSTRAINT `url_tweet_ibfk_1` FOREIGN KEY (`tweet_id`) REFERENCES `tweet` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `url_tweet_ibfk_2` FOREIGN KEY (`url_id`) REFERENCES `url` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
