#!/usr/bin/env siren v0.14
# siren_import.rb
# coding: utf-8
# Import3DCurve用

class Siren::Edge
    def first() 
        return self.param(self.sp).round(3)
    end 

    def last()
        return self.param(self.tp).round(3)
    end 
	
    def info()
        crv = self.curve
        arr = [crv.class.name]
		
        case crv.class.name
        when "Siren::Line" then
            arr << [self.sp.to_s]
            arr << [self.tp.to_s]
        when "Siren::Circle" then
            arr << [crv.center.to_s]
            arr << [crv.normal.to_s]
            arr << [crv.dir.to_s]
            arr << [crv.radius]
            arr << [self.first]
            arr << [self.last]
        when "Siren::BSCurve" then
            tmp = []
            crv.poles.each{|pos| tmp << [pos.to_s]}#.to_s.gsub(",", "$")]}
            arr << tmp.join("@")
            arr << [crv.degree]	
            arr << [crv.knots.to_s]
            arr << [crv.mults.to_s]
            arr << [crv.weights.to_s]
        else
            arr = ["non"]
        end
        return arr.join("!") + "|"
    end
end

class Siren::Vertex
    def info()
        arr = [self.class.name]
        arr << [self.to_a.to_s]
        return arr.join("!") + "|"
    end
end

comp = Siren.load_model ARGV[0]

edgelst = comp.to_a.flatten.select{|x| x.edge? == true}
edgelst.concat(comp.to_a.flatten.select {|x| x.wire? == true}.edges).flatten
edgelst.concat(comp.to_a.flatten.select {|x| x.vertex? == true})

edgelst.each{|x| puts x.info}