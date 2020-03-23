delimiter |
CREATE EVENT DBARCHIVAL
	ON SCHEDULE EVERY 1 WEEK
	STARTS CURRENT_TIMESTAMP + INTERVAL 1 DAY
	DO
		BEGIN
		UPDATE explainablecdp SET archived = 1 WHERE explainablecdp.predictionlistingid IN (SELECT predictionlistingid FROM predictionlisting WHERE timestamp < (DATE_ADD(NOW(), INTERVAL -15 DAY)));
		UPDATE predictionlisting SET archived = 1 WHERE timestamp < (DATE_ADD(NOW(), INTERVAL -15 DAY));
		DELETE FROM explainablecdp WHERE explainablecdp.archived = 1 AND explainablecdp.predictionlistingid IN (SELECT predictionlistingid FROM predictionlisting WHERE timestamp < (DATE_ADD(NOW(), INTERVAL -45 DAY)));
		DELETE FROM predictionlisting WHERE timestamp < (DATE_ADD(NOW(), INTERVAL -45 DAY)) AND archived = 1;
		END |

delimiter ;
