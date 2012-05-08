#!/usr/bin/python

import Image
import random

BYTE_LENGTH = 7

class Stegosaurus:
    
    def __init__(self, cover_img_filename, codeword):
    
        """ Accepts a GIF cover image to insert into or extract data from, depending on the object methods used.  A codeword is provided to both seed the pseudorandom number generator and to serve as the codeword for the Vigenere cipher.  Pseudorandom image coordinates are generated in the form of a list of tuples, and serve as the pixel data locations for ciphertext to be stored in their least significant bits.  Storing data within the least significant bits of pixel data will go generally unnoticed by the human eye, though attempting to store a large string will require a large number of LSBs and may be noticable. """
    
        random.seed(codeword)
        self.codeword = codeword
        self.cover_img = Image.open(cover_img_filename)
        self.pix = self.cover_img.load()
        self.pixlist = [(x, y) for x in range(0, self.cover_img.size[0]) for y in range(0, self.cover_img.size[1])]
        self.coord_list = [(x, y) for x in range(0, self.cover_img.size[0]) for y in range(0, self.cover_img.size[1])]
        random.shuffle(self.coord_list)
        self.bin_mesg = ""
        self.mesg = ""
        
    
    def repeat(self, string):
    
        """ Generator for repeating the codeword.  Used to encrypt and decrypt using Vigenere."""
        i = 0
        while True:
            yield string[i]
            i = (i + 1) % len(string)
        
    def vig_encrypt(self, plaintext):
    
        """ 
        Encrypts plaintext using the Vigenere cipher.  Uses the codeword supplied in init. 
        """
    
        r = self.repeat(self.codeword)
        ciphertext = "".join(map(lambda(x): chr((ord(x) + ord(r.next())) % 128), plaintext))
        return ciphertext
        
    def vig_decrypt(self, ciphertext):
    
        """ 
        Decrypts ciphertext using the Vigenere cipher.  Uses the codeword supplied in init. 
        """
        
        r = self.repeat(self.codeword)
        plaintext = "".join(map(lambda(x): chr((ord(x) - ord(r.next())) % 128), ciphertext))
        return plaintext
        
    def encode_bin(self, string):
    
        """
        Accepts an ASCII string and outputs its binary representation.
        """
        
        binstr = ""
        for c in string:
            binstr += bin(ord(c))[2:].rjust(BYTE_LENGTH, '0')
        return binstr
    
    def decode_bin(self, binstr):
    
    
        string = ""
        for b in range(0, len(binstr), BYTE_LENGTH):
            string += chr(int(binstr[b:b+BYTE_LENGTH], 2))
        return string
        
    def lsb_clear(self, num_bits):
            
        """ 
        Clears num_bits least significant bits from the GIF file for binary data to be stored in.  Uses the coordinate list generated upon object creation. 
        """
    
        coords = self.coord_list[:num_bits]
        for coord in coords:
            (x, y) = coord
            self.pix[x, y] = (self.pix[x, y] >> 1 << 1)  #set all lsb's in the coordinate list to zero
            
    def encode_mesg(self, mesg):
    
        """
        Attaches a header to the message string and encodes the complete message in binary.
        """
    
        header = "<" + `len(mesg)` + ">"
        return self.encode_bin(header + mesg)
            
    def hide(self, mesg):
    
        """ 
        Hides a specified message encrypted with a simple Vigenere cipher within the least significant bits of a lossless GIF file.  
        """
    
        mesg = self.vig_encrypt(mesg)
        bin_string = self.encode_mesg(mesg)
        self.bin_string = bin_string
        self.lsb_clear(len(bin_string))
        coords = list(self.coord_list)
        
        while len(bin_string) > 0:
            (x, y) = coords.pop(0)
            self.pix[x, y] = (self.pix[x, y] | int(bin_string[0]))
            bin_string = bin_string[1:]
            
    def get_length(self):
    
        """ 
        Gets the length of the message to be drawn from the GIF file.  Uses a header contained in the first bytes of the hidden string, delimited by <length>.
        """
    
        coords = list(self.coord_list)
        char = chr(int("".join([bin(self.pix[x[0], x[1]])[-1:] for x in coords[:BYTE_LENGTH]]), 2))
        length = ""
        if char == "<":
            while char != ">":
                coords = coords[BYTE_LENGTH:]
                char = chr(int("".join([bin(self.pix[x[0], x[1]])[-1:] for x in coords[:BYTE_LENGTH]]), 2))
                if char != ">": length += char
            self.coord_list = coords[BYTE_LENGTH:]
            return int(length) 
        else:
            return 0
        
    def get_bin(self, length):
        
        """ 
        Gets an encrypted binary string of specified length from the GIF file and returns it in the form of a byte-delimited string. 
        """
        
        coords = list(self.coord_list)
        bin_mesg = [bin(self.pix[x[0], x[1]])[-1:] for x in coords[:length*BYTE_LENGTH]] #get a list of the binary LSBs for our message
        bin_mesg = ["".join(bin_mesg[i:i+BYTE_LENGTH]) for i in range(0, len(bin_mesg), BYTE_LENGTH)] #group list into bytes
        return bin_mesg
       
    def bin2ascii(self, bin_list):  
        """ 
        Converts a list of byte-delimited binary strings and returns the corresponding ASCII code. 
        """
        return map(lambda(x): chr(int(x, 2)), bin_list)  #takes binary list separated into bytes and converts it to an ascii list
                    
    def show(self):
    
        """ 
        Reveals the plaintext message hidden within the GIF file.  Pulls bits from LSBs, whose locations are found in the list of coordinate tuples generated using the codeword provided upon object initialization.  Decrypts ciphertext using the Vigenere cipher with the same codeword. 
        """
        
        length = self.get_length()
        bin_list = self.get_bin(length)
        mesg = "".join(self.bin2ascii(bin_list))
        self.mesg = self.vig_decrypt(mesg)
        return self.mesg
    
    def save(self, filename):
        """
        Saves the image file to the specified filename.
        """
        self.cover_img.save(filename)
            
            
if __name__ == "__main__":
    
    print "Do you want to (read) or (write) a message?"
    opt = raw_input()
    if opt == "write":
        print "What file do you want to use to hide a message in? (Must be GIF)"
        filename = raw_input()
        print "What will be your codeword? (Save this)"
        codeword = raw_input()
        print "What will be your hidden message?"
        message = raw_input()
        print "What do you want the new filename to be?"
        new_filename = raw_input()
        
        s = Stegosaurus(filename, codeword)
        s.hide(message)
        s.save(new_filename)
    if opt == "read": 
        print "Where is the file you want to read from?"
        filename = raw_input()
        print "What is the codeword?"
        codeword = raw_input()
        
        s = Stegosaurus(filename, codeword)
        print "The hidden message is: \"" + s.show() + "\""
                
        
        
