#!/bin/bash

 (  sleep 1
    echo 'zte'
    sleep 1
    echo 'zte'
    sleep 2
    echo 'free' 
    sleep 2
    echo 'exit'
    
   )|telnet $1


