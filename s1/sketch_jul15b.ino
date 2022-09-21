
char LatDD[3],LatMM[10],LogDD[4],LogMM[10],DdMmYy[7] ,UTCTime[7];
int DayMonthYear;
char RecMessage[200];
String get1;
String A="/he1ygJ9ajyN/Location/user/update?_sn=default";
uint8_t sendATcommand(const char* ATcommand, const char* expected_answer, unsigned int timeout) {

    uint8_t x=0,  answer=0;
    char response[100];
    unsigned long previous;

    memset(response, '\0', 100);    
    
   delay(50);
    
    while( Serial.available() > 0) Serial.read();    
    
    Serial.println(ATcommand);    

    x = 0;
    previous = millis();

   delay(10);
    do{
        if(Serial.available() != 0){    
            
            response[x] = Serial.read();      
            //Serial.print(response[x]);
              x++;
            
            if (strstr(response, expected_answer) != NULL)    
            {
                answer = 1;
            }
        }
         
    }while((answer == 0) && ((millis() - previous) < timeout));
    
    return answer;
}
void GPS(){

    uint8_t answer = 0;
    bool RecNull = true;
    int i = 0;
   
    
    float Lat = 0;
    float Log = 0;
    
    memset(RecMessage, '\0', 200);    
    memset(LatDD, '\0', 3);   
    memset(LatMM, '\0', 10);  
    memset(LogDD, '\0', 4);   
    memset(LogMM, '\0', 10);    
    memset(DdMmYy, '\0', 7);   
    memset(UTCTime, '\0', 7);    

    
   

   
    sendATcommand("AT+CGPS=1,1", "OK", 50); 
    while(RecNull)
    {
        
        answer = sendATcommand("AT+CGPSINFO", "+CGPSINFO: ", 50);   
        
        if (answer == 1)
        {
            answer = 0;
            while(Serial.available() == 0);
            
            do{
                
                if(Serial.available() > 0){    
                    RecMessage[i] = Serial.read();
                    i++;
                   
                    if (strstr(RecMessage, "OK") != NULL)    
                    {
                        answer = 1;
                    }
                }
            }while(answer == 0);    
            
            RecMessage[i] = '\0';
            //Serial.println(RecMessage);
            
            MQTT();
            
            Serial.print("\n");
           
            if (strstr(RecMessage, ",,,,,,,,") != NULL) 
            {
                memset(RecMessage, '\0', 200);    
                i = 0;
                answer = 0;
               
            }
            else
            {
                RecNull = false;
                sendATcommand("AT+CGPS=0", "OK:", 50);
            } 
        }
        else
        {
            Serial.print("error \n");
            return false;
        }
       
        
    }

  
    
    return true;
    
}
void MQTT()
{
    String mystring = String(RecMessage);
    get1= mystring.substring(0, 54);
    Serial.println("AT+CMQTTSUB=0,45,1,1");
    delay(50);
    Serial.println(A);
    delay(50);
    Serial.println("AT+CMQTTTOPIC=0,45");
    delay(50);
    Serial.println(A);
    delay(50);
    Serial.println("AT+CMQTTPAYLOAD=0,56");
    delay(50);
    Serial.println(get1);
    delay(50);
    Serial.println("AT+CMQTTPUB=0,1,60");
    
    
    
    Serial.println("AT+CMQTTREL=0");

  
  
  }

void setup() {
Serial.begin(115200);
Serial.println("AT+CGPSNMEARATE=1");
delay(1000);
Serial.println("Connecting To Server........");
  
  delay(2000);
  Serial.println("AT+CMQTTSTART");
  delay(2000); 
  Serial.println("AT+CMQTTACCQ=0,\"he1ygJ9ajyN.Location|securemode=2,signmethod=hmacsha256,timestamp=1661160614654|\""); 
  delay(2000);
  Serial.println("AT+CMQTTCONNECT=0,\"tcp://iot-06z00ivuwiyka6r.mqtt.iothub.aliyuncs.com:1883\",60,1,\"Location&he1ygJ9ajyN\",\"6457f3de0efc66e6b9ac36b4db0e60c1118942bcd6bd721bc25f722918da8cc2\""); //MQTT Server Name for connecting this client
  delay(2000);
  
   
 

}

void loop() 
{
  
  GPS();

   
}
  

 
