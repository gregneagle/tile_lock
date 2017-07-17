#!/usr/bin/python
approved_UUIDs     = ['9D410000-35D6-F4DD-BA60-E7BD8DC491C0'] # see line 64
path_to_lock_sound = 'ArmingChirp.mp3'
path_to_warn_sound = 'CarAlarm.mp3'


import time
import objc
from objc import NO
from Foundation import NSBundle, NSClassFromString, NSObject, NSRunLoop, NSDate, NSUUID, NSMakeRange, NSURL
from AVFoundation import AVAudioPlayer
import Quartz

global lock_player
global warn_player

CoreBluetooth = NSBundle.bundleWithIdentifier_('com.apple.CoreBluetooth')
_ = CoreBluetooth.load()
CBCentralManager = NSClassFromString('CBCentralManager')
CBUUID = NSClassFromString('CBUUID')

constants = [
             ('CBCentralManagerScanOptionAllowDuplicatesKey', '@'),
             ('CBAdvertisementDataManufacturerDataKey', '@'),
             ('CBAdvertisementDataServiceUUIDsKey', '@'),
            ]

objc.loadBundleVariables(CoreBluetooth, globals(), constants)


Login = NSBundle.bundleWithPath_(
    '/System/Library/PrivateFrameworks/login.framework')
functions = [
             ('SACLockScreenImmediate', '@'),
            ]

objc.loadBundleFunctions(Login, globals(), functions)

# Prep the sound file
lock_sound_file = NSURL.fileURLWithPath_(path_to_lock_sound)
lock_player = AVAudioPlayer.alloc().initWithContentsOfURL_error_(
    lock_sound_file, None)
lock_player.setNumberOfLoops_(0)

# Prep the sound file
warn_sound_file = NSURL.fileURLWithPath_(path_to_warn_sound)
warn_player = AVAudioPlayer.alloc().initWithContentsOfURL_error_(
    warn_sound_file, None)
warn_player.setNumberOfLoops_(0)

class BluetoothDelegate(NSObject):
    screen_lock_time = 0.0
    def centralManager_didDiscoverPeripheral_advertisementData_RSSI_(
            self, central, peripheral, advertisement_data, rssi):
        global player
        if peripheral.name() != 'Tile':
            return
        #print "Found a Tile: identifier: ", peripheral.identifier()
        
        ad_data = advertisement_data.get(
            CBAdvertisementDataManufacturerDataKey, None)
        if ad_data != None:
            companyIDRange = NSMakeRange(0,2);
            companyIdentifier = ad_data.getBytes_range_(None, companyIDRange)
            if (ord(companyIdentifier[0]) == 0x4C):
                # print "1. got compIdentifier 0x4C"
                dataTypeRange = NSMakeRange(2,1);
                dataType = ad_data.getBytes_range_(None, dataTypeRange)
                if (ord(dataType) == 0x02):
                    # print "2. got dataType 0x02"
                    dataLengthRange = NSMakeRange(3,1);
                    dataLength = ad_data.getBytes_range_(None, dataLengthRange)
                    #print "dataLength: %s" % ord(dataLength)
                    if (ord(dataLength) == 0x15):
                        # print "3. got dataLength 0x15"
                        uuidRange = NSMakeRange(4, 16)
                        ad_bytes = ad_data.getBytes_range_(None, uuidRange)
                        # print ad_bytes
                        proximityUUID = NSUUID.alloc().initWithUUIDBytes_(
                            ad_bytes)
                        #print "proximityUUID: %s" % proximityUUID
                        # ^ uncomment this one to see beacons when you trigger them
                        #if str(proximityUUID) in approved_UUIDs:
                        if str(proximityUUID):
                            # Tile is in beacon mode; ie the button was
                            # double-clicked
                            #print "You clicked it.\n"
                            screen_status = Quartz.CGSessionCopyCurrentDictionary()
                            screen_locked = screen_status.get(
                                'CGSSessionScreenIsLocked', 0)
                            if screen_locked == 0:
                                self.screen_lock_time = time.time()
                                lock_player.play()
                                result = SACLockScreenImmediate()
                                time.sleep(2)
                                lock_player.stop()
                            else:
                                if time.time() - self.screen_lock_time > 10:
                                    warn_player.play()
                                    time.sleep(5)
                                    warn_player.stop()

    def centralManagerDidUpdateState_(self, central):
        '''Required delegate method'''
        pass


def do_it():
    delegate = BluetoothDelegate.alloc().init()
    manager = CBCentralManager.alloc().initWithDelegate_queue_(delegate, None)
    manager.scanForPeripheralsWithServices_options_(None, None)
    while True:
        try:
            NSRunLoop.currentRunLoop().runUntilDate_(
                NSDate.dateWithTimeIntervalSinceNow_(0.5))
        except (KeyboardInterrupt, SystemExit):
            break

do_it()