 CREATE OR REPLACE PROCEDURE T_Update( x IN NUMBER, y IN NUMBER) As
 BEGIN
 assume a > 0;
 assume b > 0;
 if( x >= 3) then
   update t set b = b-10 where a = y;
 END if;
 assert b > 5;
 END;
